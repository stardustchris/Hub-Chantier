"""
Use Case ExportUserData - Export RGPD Art. 20 (Portabilité des données).

Permet à un utilisateur d'exporter toutes ses données personnelles
conformément au RGPD Article 20.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from datetime import datetime, date, timedelta

from ...domain.repositories import UserRepository

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    # Interfaces des repositories externes - import uniquement pour le typage.
    # Les instances concrètes sont injectées via le constructeur (Clean Architecture).
    from modules.pointages.domain.repositories import (
        PointageRepository,
        FeuilleHeuresRepository,
    )
    from modules.planning.domain.repositories import AffectationRepository
    from modules.dashboard.domain.repositories import (
        PostRepository,
        CommentRepository,
        LikeRepository,
    )
    from modules.documents.domain.repositories import (
        DocumentRepository,
        AutorisationRepository,
    )
    from modules.formulaires.domain.repositories import FormulaireRempliRepository
    from modules.signalements.domain.repositories import (
        SignalementRepository,
        ReponseRepository,
    )
    from modules.interventions.domain.repositories import (
        InterventionRepository,
        AffectationInterventionRepository,
        InterventionMessageRepository,
    )
    from modules.shared.domain.repositories import AuditRepository


class ExportUserDataUseCase:
    """
    Cas d'utilisation : Exporter toutes les données personnelles d'un utilisateur.

    Conformité RGPD Article 20 - Droit à la portabilité des données.

    Un utilisateur peut demander l'export complet de toutes ses données
    personnelles dans un format structuré, couramment utilisé et
    lisible par machine (JSON).

    Attributes:
        user_repo: Repository des utilisateurs.
        pointage_repo: Repository des pointages.
        feuille_heures_repo: Repository des feuilles d'heures.
        affectation_repo: Repository des affectations planning.
        post_repo: Repository des posts dashboard.
        comment_repo: Repository des commentaires dashboard.
        like_repo: Repository des likes dashboard.
        document_repo: Repository des documents.
        autorisation_repo: Repository des autorisations documents.
        formulaire_repo: Repository des formulaires remplis.
        signalement_repo: Repository des signalements.
        reponse_repo: Repository des réponses signalements.
        intervention_repo: Repository des interventions.
        affectation_intervention_repo: Repository des affectations interventions.
        message_intervention_repo: Repository des messages interventions.
        audit_repo: Repository des entrées d'audit.
    """

    def __init__(
        self,
        user_repo: UserRepository,
        pointage_repo: Optional[PointageRepository] = None,
        feuille_heures_repo: Optional[FeuilleHeuresRepository] = None,
        affectation_repo: Optional[AffectationRepository] = None,
        post_repo: Optional[PostRepository] = None,
        comment_repo: Optional[CommentRepository] = None,
        like_repo: Optional[LikeRepository] = None,
        document_repo: Optional[DocumentRepository] = None,
        autorisation_repo: Optional[AutorisationRepository] = None,
        formulaire_repo: Optional[FormulaireRempliRepository] = None,
        signalement_repo: Optional[SignalementRepository] = None,
        reponse_repo: Optional[ReponseRepository] = None,
        intervention_repo: Optional[InterventionRepository] = None,
        affectation_intervention_repo: Optional[AffectationInterventionRepository] = None,
        message_intervention_repo: Optional[InterventionMessageRepository] = None,
        audit_repo: Optional[AuditRepository] = None,
    ):
        """
        Initialise le use case.

        Args:
            user_repo: Repository utilisateurs (interface, obligatoire).
            pointage_repo: Repository pointages (optionnel).
            feuille_heures_repo: Repository feuilles d'heures (optionnel).
            affectation_repo: Repository affectations planning (optionnel).
            post_repo: Repository posts dashboard (optionnel).
            comment_repo: Repository commentaires dashboard (optionnel).
            like_repo: Repository likes dashboard (optionnel).
            document_repo: Repository documents (optionnel).
            autorisation_repo: Repository autorisations documents (optionnel).
            formulaire_repo: Repository formulaires remplis (optionnel).
            signalement_repo: Repository signalements (optionnel).
            reponse_repo: Repository réponses signalements (optionnel).
            intervention_repo: Repository interventions (optionnel).
            affectation_intervention_repo: Repository affectations interventions (optionnel).
            message_intervention_repo: Repository messages interventions (optionnel).
            audit_repo: Repository audit (optionnel).
        """
        self.user_repo = user_repo
        self.pointage_repo = pointage_repo
        self.feuille_heures_repo = feuille_heures_repo
        self.affectation_repo = affectation_repo
        self.post_repo = post_repo
        self.comment_repo = comment_repo
        self.like_repo = like_repo
        self.document_repo = document_repo
        self.autorisation_repo = autorisation_repo
        self.formulaire_repo = formulaire_repo
        self.signalement_repo = signalement_repo
        self.reponse_repo = reponse_repo
        self.intervention_repo = intervention_repo
        self.affectation_intervention_repo = affectation_intervention_repo
        self.message_intervention_repo = message_intervention_repo
        self.audit_repo = audit_repo

    def execute(self, user_id: int) -> Dict[str, Any]:
        """
        Exporte toutes les données personnelles de l'utilisateur.

        Args:
            user_id: ID de l'utilisateur demandant l'export.

        Returns:
            Dictionnaire structuré avec toutes les données personnelles:
            - Profil utilisateur (nom, prenom, email, telephone, etc.)
            - Pointages et heures travaillées
            - Affectations planning
            - Posts et commentaires
            - Documents uploadés
            - Formulaires remplis
            - Signalements créés
            - Interventions assignées

        Raises:
            UserNotFoundError: Si l'utilisateur n'existe pas.
        """
        # Récupérer l'utilisateur
        user = self.user_repo.find_by_id(user_id)
        if not user:
            from ...application.use_cases import UserNotFoundError
            raise UserNotFoundError(f"Utilisateur {user_id} introuvable")

        # Structure de données complète
        # Chaque section est wrappée en try/except pour qu'une erreur
        # sur un module ne bloque pas l'export des autres données.
        errors: List[str] = []

        export_data: Dict[str, Any] = {
            "export_info": {
                "date_export": datetime.now().isoformat(),
                "user_id": user.id,
                "format": "JSON",
                "rgpd_article": "Article 20 - Portabilité des données",
            },
        }

        # Profil (obligatoire, pas de try/except car données déjà chargées)
        export_data["profil"] = self._export_profil(user)

        # Activité (audit logs)
        try:
            export_data["activite"] = self._export_activite(user_id)
        except Exception as e:
            logger.error("Erreur lors de l'export des données d'activité pour l'utilisateur %s: %s", user_id, e)
            errors.append("activite")
            export_data["activite"] = {"erreur": "Données d'activité temporairement indisponibles"}

        # Planning (affectations)
        try:
            export_data["planning"] = self._export_planning(user_id)
        except Exception as e:
            logger.error("Erreur lors de l'export du planning pour l'utilisateur %s: %s", user_id, e)
            errors.append("planning")
            export_data["planning"] = {"erreur": "Données de planning temporairement indisponibles"}

        # Pointages et heures
        try:
            export_data["pointages"] = self._export_pointages(user_id)
        except Exception as e:
            logger.error("Erreur lors de l'export des pointages pour l'utilisateur %s: %s", user_id, e)
            errors.append("pointages")
            export_data["pointages"] = {"erreur": "Données de pointages temporairement indisponibles"}

        # Contenu (posts, commentaires, likes)
        try:
            export_data["contenu"] = self._export_contenu(user_id)
        except Exception as e:
            logger.error("Erreur lors de l'export du contenu pour l'utilisateur %s: %s", user_id, e)
            errors.append("contenu")
            export_data["contenu"] = {"erreur": "Données de contenu temporairement indisponibles"}

        # Documents
        try:
            export_data["documents"] = self._export_documents(user_id)
        except Exception as e:
            logger.error("Erreur lors de l'export des documents pour l'utilisateur %s: %s", user_id, e)
            errors.append("documents")
            export_data["documents"] = {"erreur": "Données de documents temporairement indisponibles"}

        # Formulaires
        try:
            export_data["formulaires"] = self._export_formulaires(user_id)
        except Exception as e:
            logger.error("Erreur lors de l'export des formulaires pour l'utilisateur %s: %s", user_id, e)
            errors.append("formulaires")
            export_data["formulaires"] = {"erreur": "Données de formulaires temporairement indisponibles"}

        # Signalements
        try:
            export_data["signalements"] = self._export_signalements(user_id)
        except Exception as e:
            logger.error("Erreur lors de l'export des signalements pour l'utilisateur %s: %s", user_id, e)
            errors.append("signalements")
            export_data["signalements"] = {"erreur": "Données de signalements temporairement indisponibles"}

        # Interventions
        try:
            export_data["interventions"] = self._export_interventions(user_id)
        except Exception as e:
            logger.error("Erreur lors de l'export des interventions pour l'utilisateur %s: %s", user_id, e)
            errors.append("interventions")
            export_data["interventions"] = {"erreur": "Données d'interventions temporairement indisponibles"}

        # Ajouter les erreurs à l'export_info si applicable
        if errors:
            export_data["export_info"]["sections_en_erreur"] = errors
            export_data["export_info"]["note"] = (
                "Certaines sections n'ont pas pu être exportées. "
                "Veuillez réessayer ultérieurement."
            )

        return export_data

    def _export_profil(self, user) -> Dict[str, Any]:
        """Exporte les données du profil utilisateur."""
        return {
            "id": user.id,
            "email": user.email,
            "nom": user.nom,
            "prenom": user.prenom,
            "telephone": user.telephone,
            "role": user.role,
            "type_utilisateur": user.type_utilisateur,
            "metiers": user.metiers,
            "taux_horaire": float(user.taux_horaire) if user.taux_horaire else None,
            "code_utilisateur": user.code_utilisateur,
            "couleur": user.couleur,
            "photo_profil": user.photo_profil,
            "contact_urgence_nom": user.contact_urgence_nom,
            "contact_urgence_tel": user.contact_urgence_tel,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }

    def _export_activite(self, user_id: int) -> Dict[str, Any]:
        """Exporte les données d'activité (connexions, audit logs)."""
        if not self.audit_repo:
            return {
                "connexions": [],
                "actions": [],
                "note": "Les logs d'audit sont conservés 30 jours conformément RGPD",
            }

        # Récupérer les actions des 30 derniers jours
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        entries = self.audit_repo.get_user_actions(
            author_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=500,
        )

        actions = [
            {
                "id": str(entry.id),
                "entity_type": entry.entity_type,
                "entity_id": entry.entity_id,
                "action": entry.action,
                "field_name": entry.field_name,
                "timestamp": entry.timestamp.isoformat() if entry.timestamp else None,
                "motif": entry.motif,
            }
            for entry in entries
        ]

        return {
            "connexions": [],
            "actions": actions,
            "note": "Les logs d'audit sont conservés 30 jours conformément RGPD",
        }

    def _export_planning(self, user_id: int) -> Dict[str, Any]:
        """Exporte les affectations planning."""
        if not self.affectation_repo:
            return {
                "affectations": [],
                "note": "Affectations des 12 derniers mois",
            }

        # Récupérer les affectations des 12 derniers mois
        date_fin = date.today()
        date_debut = date_fin - timedelta(days=365)
        affectations = self.affectation_repo.find_by_utilisateur(
            utilisateur_id=user_id,
            date_debut=date_debut,
            date_fin=date_fin,
        )

        affectations_data = [
            {
                "id": a.id,
                "chantier_id": a.chantier_id,
                "date": a.date.isoformat(),
                "heures_prevues": a.heures_prevues,
                "heure_debut": str(a.heure_debut) if a.heure_debut else None,
                "heure_fin": str(a.heure_fin) if a.heure_fin else None,
                "note": a.note,
                "type_affectation": a.type_affectation.value if a.type_affectation else None,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in affectations
        ]

        return {
            "affectations": affectations_data,
            "note": "Affectations des 12 derniers mois",
        }

    def _export_pointages(self, user_id: int) -> Dict[str, Any]:
        """Exporte les pointages et heures travaillées."""
        pointages_data: List[Dict[str, Any]] = []
        feuilles_data: List[Dict[str, Any]] = []

        # Pointages des 24 derniers mois
        if self.pointage_repo:
            date_fin = date.today()
            date_debut = date_fin - timedelta(days=730)
            pointages, _ = self.pointage_repo.search(
                utilisateur_id=user_id,
                date_debut=date_debut,
                date_fin=date_fin,
                limit=5000,
            )

            pointages_data = [
                {
                    "id": p.id,
                    "chantier_id": p.chantier_id,
                    "date_pointage": p.date_pointage.isoformat(),
                    "heures_normales": str(p.heures_normales),
                    "heures_supplementaires": str(p.heures_supplementaires),
                    "statut": p.statut.value if p.statut else None,
                    "commentaire": p.commentaire,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                }
                for p in pointages
            ]

        # Feuilles d'heures
        if self.feuille_heures_repo:
            feuilles, _ = self.feuille_heures_repo.find_by_utilisateur(
                utilisateur_id=user_id,
                limit=200,
            )

            feuilles_data = [
                {
                    "id": f.id,
                    "annee": f.annee,
                    "numero_semaine": f.numero_semaine,
                    "semaine_debut": f.semaine_debut.isoformat(),
                    "statut_global": f.statut_global.value if f.statut_global else None,
                    "total_heures": f.total_heures_decimal,
                    "commentaire_global": f.commentaire_global,
                    "created_at": f.created_at.isoformat() if f.created_at else None,
                }
                for f in feuilles
            ]

        return {
            "pointages": pointages_data,
            "feuilles_heures": feuilles_data,
            "note": "Données des 24 derniers mois",
        }

    def _export_contenu(self, user_id: int) -> Dict[str, Any]:
        """Exporte les posts et commentaires."""
        posts_data: List[Dict[str, Any]] = []
        commentaires_data: List[Dict[str, Any]] = []
        likes_data: List[Dict[str, Any]] = []

        # Posts
        if self.post_repo:
            posts = self.post_repo.find_by_author(
                author_id=user_id,
                limit=500,
            )
            posts_data = [
                {
                    "id": p.id,
                    "content": p.content,
                    "status": p.status.value if p.status else None,
                    "is_urgent": p.is_urgent,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                }
                for p in posts
            ]

        # Commentaires
        if self.comment_repo:
            commentaires = self.comment_repo.find_by_author(author_id=user_id)
            commentaires_data = [
                {
                    "id": c.id,
                    "post_id": c.post_id,
                    "content": c.content,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
                for c in commentaires
            ]

        # Likes
        if self.like_repo:
            likes = self.like_repo.find_by_user(user_id=user_id)
            likes_data = [
                {
                    "id": lk.id,
                    "post_id": lk.post_id,
                    "created_at": lk.created_at.isoformat() if lk.created_at else None,
                }
                for lk in likes
            ]

        return {
            "posts": posts_data,
            "commentaires": commentaires_data,
            "likes": likes_data,
        }

    def _export_documents(self, user_id: int) -> Dict[str, Any]:
        """Exporte les métadonnées des documents uploadés."""
        documents_data: List[Dict[str, Any]] = []
        autorisations_data: List[Dict[str, Any]] = []

        # Documents uploadés par l'utilisateur
        if self.document_repo:
            documents = self.document_repo.find_by_uploaded_by(
                user_id=user_id,
                limit=500,
            )
            documents_data = [
                {
                    "id": d.id,
                    "nom": d.nom,
                    "nom_original": d.nom_original,
                    "type_document": d.type_document.value if d.type_document else None,
                    "taille": d.taille,
                    "mime_type": d.mime_type,
                    "chantier_id": d.chantier_id,
                    "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
                }
                for d in documents
            ]

        # Autorisations nominatives de l'utilisateur
        if self.autorisation_repo:
            autorisations = self.autorisation_repo.find_by_user(user_id=user_id)
            autorisations_data = [
                {
                    "id": a.id,
                    "type_autorisation": a.type_autorisation.value if a.type_autorisation else None,
                    "cible": a.cible,
                    "cible_id": a.cible_id,
                    "created_at": a.created_at.isoformat() if a.created_at else None,
                    "expire_at": a.expire_at.isoformat() if a.expire_at else None,
                }
                for a in autorisations
            ]

        return {
            "documents_uploades": documents_data,
            "autorisations": autorisations_data,
            "note": "Métadonnées uniquement. Les fichiers sont téléchargeables via l'application.",
        }

    def _export_formulaires(self, user_id: int) -> Dict[str, Any]:
        """Exporte les formulaires remplis."""
        if not self.formulaire_repo:
            return {
                "formulaires_remplis": [],
            }

        formulaires = self.formulaire_repo.find_by_user(
            user_id=user_id,
            limit=500,
        )

        formulaires_data = [
            {
                "id": f.id,
                "template_id": f.template_id,
                "chantier_id": f.chantier_id,
                "statut": f.statut.value if f.statut else None,
                "version": f.version,
                "soumis_at": f.soumis_at.isoformat() if f.soumis_at else None,
                "created_at": f.created_at.isoformat() if f.created_at else None,
            }
            for f in formulaires
        ]

        return {
            "formulaires_remplis": formulaires_data,
        }

    def _export_signalements(self, user_id: int) -> Dict[str, Any]:
        """Exporte les signalements créés."""
        signalements_data: List[Dict[str, Any]] = []
        reponses_data: List[Dict[str, Any]] = []

        # Signalements créés par l'utilisateur
        if self.signalement_repo:
            signalements = self.signalement_repo.find_by_createur(
                user_id=user_id,
                limit=500,
            )
            signalements_data = [
                {
                    "id": s.id,
                    "chantier_id": s.chantier_id,
                    "titre": s.titre,
                    "description": s.description,
                    "priorite": s.priorite.value if s.priorite else None,
                    "statut": s.statut.value if s.statut else None,
                    "localisation": s.localisation,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                }
                for s in signalements
            ]

        # Réponses de l'utilisateur sur des signalements
        if self.reponse_repo:
            reponses = self.reponse_repo.find_by_auteur(
                auteur_id=user_id,
                limit=500,
            )
            reponses_data = [
                {
                    "id": r.id,
                    "signalement_id": r.signalement_id,
                    "contenu": r.contenu,
                    "est_resolution": r.est_resolution,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in reponses
            ]

        return {
            "signalements_crees": signalements_data,
            "reponses_signalements": reponses_data,
        }

    def _export_interventions(self, user_id: int) -> Dict[str, Any]:
        """Exporte les interventions assignées."""
        interventions_data: List[Dict[str, Any]] = []
        messages_data: List[Dict[str, Any]] = []

        # Interventions affectées à l'utilisateur
        if self.intervention_repo:
            interventions = self.intervention_repo.list_by_utilisateur(
                utilisateur_id=user_id,
            )
            interventions_data = [
                {
                    "id": i.id,
                    "code": i.code,
                    "type_intervention": i.type_intervention.value if i.type_intervention else None,
                    "statut": i.statut.value if i.statut else None,
                    "priorite": i.priorite.value if i.priorite else None,
                    "client_nom": i.client_nom,
                    "description": i.description,
                    "date_planifiee": i.date_planifiee.isoformat() if i.date_planifiee else None,
                    "travaux_realises": i.travaux_realises,
                    "created_at": i.created_at.isoformat() if i.created_at else None,
                }
                for i in interventions
            ]

            # Messages de l'utilisateur sur ces interventions
            # Requête groupée pour éviter le N+1
            if self.message_intervention_repo and interventions:
                intervention_ids = [
                    i.id for i in interventions if i.id is not None
                ]
                if intervention_ids:
                    all_msgs = self.message_intervention_repo.list_by_interventions(
                        intervention_ids=intervention_ids,
                        auteur_id=user_id,
                        limit=500,
                    )
                    messages_data = [
                        {
                            "id": m.id,
                            "intervention_id": m.intervention_id,
                            "type_message": m.type_message.value if m.type_message else None,
                            "contenu": m.contenu,
                            "created_at": m.created_at.isoformat() if m.created_at else None,
                        }
                        for m in all_msgs
                    ]

        return {
            "interventions_assignees": interventions_data,
            "messages": messages_data,
        }
