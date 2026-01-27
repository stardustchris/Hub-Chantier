"""
Use Case ExportUserData - Export RGPD Art. 20 (Portabilité des données).

Permet à un utilisateur d'exporter toutes ses données personnelles
conformément au RGPD Article 20.
"""

from typing import Dict, Any, List
from datetime import datetime

from ...domain.repositories import UserRepository


class ExportUserDataUseCase:
    """
    Cas d'utilisation : Exporter toutes les données personnelles d'un utilisateur.

    Conformité RGPD Article 20 - Droit à la portabilité des données.

    Un utilisateur peut demander l'export complet de toutes ses données
    personnelles dans un format structuré, couramment utilisé et
    lisible par machine (JSON).

    Attributes:
        user_repo: Repository des utilisateurs.
    """

    def __init__(self, user_repo: UserRepository):
        """
        Initialise le use case.

        Args:
            user_repo: Repository utilisateurs (interface).
        """
        self.user_repo = user_repo

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
        export_data = {
            "export_info": {
                "date_export": datetime.now().isoformat(),
                "user_id": user.id,
                "format": "JSON",
                "rgpd_article": "Article 20 - Portabilité des données",
            },
            "profil": self._export_profil(user),
            "activite": self._export_activite(user_id),
            "planning": self._export_planning(user_id),
            "pointages": self._export_pointages(user_id),
            "contenu": self._export_contenu(user_id),
            "documents": self._export_documents(user_id),
            "formulaires": self._export_formulaires(user_id),
            "signalements": self._export_signalements(user_id),
            "interventions": self._export_interventions(user_id),
        }

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
            "metier": user.metier,
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
        # TODO: Implémenter récupération depuis audit_logs
        # Pour l'instant, retourner structure vide
        return {
            "connexions": [],
            "actions": [],
            "note": "Les logs d'audit sont conservés 30 jours conformément RGPD",
        }

    def _export_planning(self, user_id: int) -> Dict[str, Any]:
        """Exporte les affectations planning."""
        # TODO: Implémenter récupération depuis planning
        return {
            "affectations": [],
            "note": "Affectations des 12 derniers mois",
        }

    def _export_pointages(self, user_id: int) -> Dict[str, Any]:
        """Exporte les pointages et heures travaillées."""
        # TODO: Implémenter récupération depuis pointages
        return {
            "pointages": [],
            "feuilles_heures": [],
            "note": "Données des 24 derniers mois",
        }

    def _export_contenu(self, user_id: int) -> Dict[str, Any]:
        """Exporte les posts et commentaires."""
        # TODO: Implémenter récupération depuis dashboard
        return {
            "posts": [],
            "commentaires": [],
            "likes": [],
        }

    def _export_documents(self, user_id: int) -> Dict[str, Any]:
        """Exporte les métadonnées des documents uploadés."""
        # TODO: Implémenter récupération depuis documents
        # Note: On exporte les métadonnées, pas les fichiers eux-mêmes
        return {
            "documents_uploades": [],
            "autorisations": [],
            "note": "Métadonnées uniquement. Les fichiers sont téléchargeables via l'application.",
        }

    def _export_formulaires(self, user_id: int) -> Dict[str, Any]:
        """Exporte les formulaires remplis."""
        # TODO: Implémenter récupération depuis formulaires
        return {
            "formulaires_remplis": [],
        }

    def _export_signalements(self, user_id: int) -> Dict[str, Any]:
        """Exporte les signalements créés."""
        # TODO: Implémenter récupération depuis signalements
        return {
            "signalements_crees": [],
            "reponses_signalements": [],
        }

    def _export_interventions(self, user_id: int) -> Dict[str, Any]:
        """Exporte les interventions assignées."""
        # TODO: Implémenter récupération depuis interventions
        return {
            "interventions_assignees": [],
            "messages": [],
        }
