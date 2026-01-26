"""Implémentation SQLAlchemy du repository Signalement."""

from datetime import datetime, timedelta
from typing import Optional, List, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import func, or_, case

from .models import SignalementModel
from ...domain.entities import Signalement
from ...domain.repositories import SignalementRepository
from ...domain.value_objects import Priorite, StatutSignalement


class SQLAlchemySignalementRepository(SignalementRepository):
    """Implémentation SQLAlchemy du repository Signalement."""

    def __init__(self, session: Session):
        """
        Initialise le repository.

        Args:
            session: Session SQLAlchemy.
        """
        self._session = session

    def find_by_id(self, signalement_id: int) -> Optional[Signalement]:
        """Trouve un signalement par son ID."""
        model = self._session.query(SignalementModel).filter(
            SignalementModel.id == signalement_id
        ).first()

        if not model:
            return None

        return self._to_entity(model)

    def save(self, signalement: Signalement) -> Signalement:
        """Persiste un signalement."""
        if signalement.id is None:
            # Création
            model = SignalementModel(
                chantier_id=signalement.chantier_id,
                titre=signalement.titre,
                description=signalement.description,
                priorite=signalement.priorite.value,
                statut=signalement.statut.value,
                cree_par=signalement.cree_par,
                assigne_a=signalement.assigne_a,
                date_resolution_souhaitee=signalement.date_resolution_souhaitee,
                date_traitement=signalement.date_traitement,
                date_cloture=signalement.date_cloture,
                commentaire_traitement=signalement.commentaire_traitement,
                photo_url=signalement.photo_url,
                localisation=signalement.localisation,
                nb_escalades=signalement.nb_escalades,
                derniere_escalade_at=signalement.derniere_escalade_at,
                created_at=signalement.created_at,
                updated_at=signalement.updated_at,
            )
            self._session.add(model)
            self._session.commit()
            self._session.refresh(model)
            signalement.id = model.id
        else:
            # Mise à jour
            model = self._session.query(SignalementModel).filter(
                SignalementModel.id == signalement.id
            ).first()

            if model:
                model.titre = signalement.titre
                model.description = signalement.description
                model.priorite = signalement.priorite.value
                model.statut = signalement.statut.value
                model.assigne_a = signalement.assigne_a
                model.date_resolution_souhaitee = signalement.date_resolution_souhaitee
                model.date_traitement = signalement.date_traitement
                model.date_cloture = signalement.date_cloture
                model.commentaire_traitement = signalement.commentaire_traitement
                model.photo_url = signalement.photo_url
                model.localisation = signalement.localisation
                model.nb_escalades = signalement.nb_escalades
                model.derniere_escalade_at = signalement.derniere_escalade_at
                model.updated_at = datetime.now()
                self._session.commit()

        return signalement

    def delete(self, signalement_id: int) -> bool:
        """Supprime un signalement."""
        result = self._session.query(SignalementModel).filter(
            SignalementModel.id == signalement_id
        ).delete()
        self._session.commit()
        return result > 0

    def find_by_chantier(
        self,
        chantier_id: int,
        skip: int = 0,
        limit: int = 100,
        statut: Optional[StatutSignalement] = None,
        priorite: Optional[Priorite] = None,
    ) -> List[Signalement]:
        """Récupère les signalements d'un chantier."""
        query = self._session.query(SignalementModel).filter(
            SignalementModel.chantier_id == chantier_id
        )

        if statut:
            query = query.filter(SignalementModel.statut == statut.value)

        if priorite:
            query = query.filter(SignalementModel.priorite == priorite.value)

        # Tri par priorité puis par date de création (plus récent en premier)
        # Utilise CASE WHEN pour compatibilité SQLite/PostgreSQL (pas de func.field)
        priority_order = case(
            (SignalementModel.priorite == "critique", 1),
            (SignalementModel.priorite == "haute", 2),
            (SignalementModel.priorite == "moyenne", 3),
            (SignalementModel.priorite == "basse", 4),
            else_=5
        )
        query = query.order_by(
            priority_order,
            SignalementModel.created_at.desc(),
        )

        models = query.offset(skip).limit(limit).all()
        return [self._to_entity(m) for m in models]

    def find_all(
        self,
        skip: int = 0,
        limit: int = 100,
        chantier_ids: Optional[List[int]] = None,
        statut: Optional[StatutSignalement] = None,
        priorite: Optional[Priorite] = None,
        date_debut: Optional[datetime] = None,
        date_fin: Optional[datetime] = None,
    ) -> Tuple[List[Signalement], int]:
        """Récupère tous les signalements avec filtres."""
        query = self._session.query(SignalementModel)

        if chantier_ids:
            query = query.filter(SignalementModel.chantier_id.in_(chantier_ids))

        if statut:
            query = query.filter(SignalementModel.statut == statut.value)

        if priorite:
            query = query.filter(SignalementModel.priorite == priorite.value)

        if date_debut:
            query = query.filter(SignalementModel.created_at >= date_debut)

        if date_fin:
            query = query.filter(SignalementModel.created_at <= date_fin)

        total = query.count()

        query = query.order_by(SignalementModel.created_at.desc())
        models = query.offset(skip).limit(limit).all()

        return [self._to_entity(m) for m in models], total

    def find_by_createur(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Signalement]:
        """Récupère les signalements créés par un utilisateur."""
        models = self._session.query(SignalementModel).filter(
            SignalementModel.cree_par == user_id
        ).order_by(
            SignalementModel.created_at.desc()
        ).offset(skip).limit(limit).all()

        return [self._to_entity(m) for m in models]

    def find_assignes_a(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Signalement]:
        """Récupère les signalements assignés à un utilisateur."""
        models = self._session.query(SignalementModel).filter(
            SignalementModel.assigne_a == user_id
        ).order_by(
            SignalementModel.created_at.desc()
        ).offset(skip).limit(limit).all()

        return [self._to_entity(m) for m in models]

    def count_by_chantier(
        self,
        chantier_id: int,
        statut: Optional[StatutSignalement] = None,
        priorite: Optional[Priorite] = None,
    ) -> int:
        """Compte le nombre de signalements dans un chantier."""
        query = self._session.query(func.count(SignalementModel.id)).filter(
            SignalementModel.chantier_id == chantier_id
        )

        if statut:
            query = query.filter(SignalementModel.statut == statut.value)

        if priorite:
            query = query.filter(SignalementModel.priorite == priorite.value)

        return query.scalar() or 0

    def count_by_statut(self, chantier_id: Optional[int] = None) -> dict:
        """Compte les signalements par statut."""
        query = self._session.query(
            SignalementModel.statut,
            func.count(SignalementModel.id)
        )

        if chantier_id:
            query = query.filter(SignalementModel.chantier_id == chantier_id)

        query = query.group_by(SignalementModel.statut)
        results = query.all()

        return {statut: count for statut, count in results}

    def count_by_priorite(self, chantier_id: Optional[int] = None) -> dict:
        """Compte les signalements par priorité."""
        query = self._session.query(
            SignalementModel.priorite,
            func.count(SignalementModel.id)
        )

        if chantier_id:
            query = query.filter(SignalementModel.chantier_id == chantier_id)

        query = query.group_by(SignalementModel.priorite)
        results = query.all()

        return {priorite: count for priorite, count in results}

    def find_en_retard(
        self,
        chantier_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Signalement]:
        """Récupère les signalements en retard."""
        datetime.now()

        # Signalements actifs (non résolus)
        query = self._session.query(SignalementModel).filter(
            SignalementModel.statut.in_(["ouvert", "en_cours"])
        )

        if chantier_id:
            query = query.filter(SignalementModel.chantier_id == chantier_id)

        models = query.order_by(SignalementModel.created_at).all()

        # Filtrer en retard côté Python pour la logique complexe
        en_retard = []
        for model in models:
            entity = self._to_entity(model)
            if entity.est_en_retard:
                en_retard.append(entity)

        return en_retard[skip:skip + limit]

    def find_a_escalader(
        self,
        seuil_pourcentage: float = 50.0,
    ) -> List[Signalement]:
        """Récupère les signalements nécessitant une escalade."""
        # Signalements actifs
        models = self._session.query(SignalementModel).filter(
            SignalementModel.statut.in_(["ouvert", "en_cours"])
        ).all()

        # Filtrer selon le pourcentage
        a_escalader = []
        for model in models:
            entity = self._to_entity(model)
            if entity.pourcentage_temps_ecoule >= seuil_pourcentage:
                a_escalader.append(entity)

        return a_escalader

    def search(
        self,
        query: str,
        chantier_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Signalement], int]:
        """Recherche des signalements par texte."""
        search_query = self._session.query(SignalementModel).filter(
            or_(
                SignalementModel.titre.ilike(f"%{query}%"),
                SignalementModel.description.ilike(f"%{query}%"),
                SignalementModel.localisation.ilike(f"%{query}%"),
            )
        )

        if chantier_id:
            search_query = search_query.filter(
                SignalementModel.chantier_id == chantier_id
            )

        total = search_query.count()

        models = search_query.order_by(
            SignalementModel.created_at.desc()
        ).offset(skip).limit(limit).all()

        return [self._to_entity(m) for m in models], total

    def get_statistiques(
        self,
        chantier_id: Optional[int] = None,
        date_debut: Optional[datetime] = None,
        date_fin: Optional[datetime] = None,
    ) -> dict:
        """Récupère les statistiques des signalements."""
        query = self._session.query(SignalementModel)

        if chantier_id:
            query = query.filter(SignalementModel.chantier_id == chantier_id)

        if date_debut:
            query = query.filter(SignalementModel.created_at >= date_debut)

        if date_fin:
            query = query.filter(SignalementModel.created_at <= date_fin)

        models = query.all()

        # Calculer les statistiques
        total = len(models)
        par_statut = {}
        par_priorite = {}
        en_retard = 0
        traites_cette_semaine = 0
        temps_resolutions = []

        now = datetime.now()
        debut_semaine = now - timedelta(days=now.weekday())

        for model in models:
            # Comptage par statut
            par_statut[model.statut] = par_statut.get(model.statut, 0) + 1

            # Comptage par priorité
            par_priorite[model.priorite] = par_priorite.get(model.priorite, 0) + 1

            # En retard
            entity = self._to_entity(model)
            if entity.est_en_retard:
                en_retard += 1

            # Traités cette semaine
            if model.date_traitement and model.date_traitement >= debut_semaine:
                traites_cette_semaine += 1

            # Temps de résolution
            if model.date_traitement and model.created_at:
                duree = (model.date_traitement - model.created_at).total_seconds() / 3600
                temps_resolutions.append(duree)

        # Temps moyen de résolution
        temps_moyen = None
        if temps_resolutions:
            temps_moyen = sum(temps_resolutions) / len(temps_resolutions)

        # Taux de résolution
        resolus = par_statut.get("traite", 0) + par_statut.get("cloture", 0)
        taux_resolution = (resolus / total * 100) if total > 0 else 0.0

        return {
            "total": total,
            "par_statut": par_statut,
            "par_priorite": par_priorite,
            "en_retard": en_retard,
            "traites_cette_semaine": traites_cette_semaine,
            "temps_moyen_resolution": temps_moyen,
            "taux_resolution": taux_resolution,
        }

    def _to_entity(self, model: SignalementModel) -> Signalement:
        """Convertit un modèle SQLAlchemy en entité de domaine."""
        return Signalement(
            id=model.id,
            chantier_id=model.chantier_id,
            titre=model.titre,
            description=model.description,
            priorite=Priorite(model.priorite),
            statut=StatutSignalement(model.statut),
            cree_par=model.cree_par,
            assigne_a=model.assigne_a,
            date_resolution_souhaitee=model.date_resolution_souhaitee,
            date_traitement=model.date_traitement,
            date_cloture=model.date_cloture,
            commentaire_traitement=model.commentaire_traitement,
            photo_url=model.photo_url,
            localisation=model.localisation,
            nb_escalades=model.nb_escalades,
            derniere_escalade_at=model.derniere_escalade_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
