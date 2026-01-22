"""Implementation SQLAlchemy du FeuilleTacheRepository."""

from datetime import date
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy import func

from ...domain.entities import FeuilleTache
from ...domain.entities.feuille_tache import StatutValidation
from ...domain.repositories import FeuilleTacheRepository
from .feuille_tache_model import FeuilleTacheModel


class SQLAlchemyFeuilleTacheRepository(FeuilleTacheRepository):
    """
    Implementation SQLAlchemy du repository FeuilleTache.

    Gere la persistence des feuilles de taches (TAC-18, TAC-19).
    """

    def __init__(self, session: Session):
        """
        Initialise le repository.

        Args:
            session: Session SQLAlchemy.
        """
        self.session = session

    def find_by_id(self, feuille_id: int) -> Optional[FeuilleTache]:
        """Trouve une feuille par son ID."""
        model = (
            self.session.query(FeuilleTacheModel)
            .filter(FeuilleTacheModel.id == feuille_id)
            .first()
        )
        return model.to_entity() if model else None

    def find_by_tache(
        self,
        tache_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FeuilleTache]:
        """Trouve les feuilles d'une tache."""
        models = (
            self.session.query(FeuilleTacheModel)
            .filter(FeuilleTacheModel.tache_id == tache_id)
            .order_by(FeuilleTacheModel.date_travail.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [m.to_entity() for m in models]

    def find_by_utilisateur(
        self,
        utilisateur_id: int,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FeuilleTache]:
        """Trouve les feuilles d'un utilisateur."""
        query = self.session.query(FeuilleTacheModel).filter(
            FeuilleTacheModel.utilisateur_id == utilisateur_id
        )

        if date_debut:
            query = query.filter(FeuilleTacheModel.date_travail >= date_debut)
        if date_fin:
            query = query.filter(FeuilleTacheModel.date_travail <= date_fin)

        models = (
            query.order_by(FeuilleTacheModel.date_travail.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [m.to_entity() for m in models]

    def find_by_chantier(
        self,
        chantier_id: int,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        statut: Optional[StatutValidation] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FeuilleTache]:
        """Trouve les feuilles d'un chantier."""
        query = self.session.query(FeuilleTacheModel).filter(
            FeuilleTacheModel.chantier_id == chantier_id
        )

        if date_debut:
            query = query.filter(FeuilleTacheModel.date_travail >= date_debut)
        if date_fin:
            query = query.filter(FeuilleTacheModel.date_travail <= date_fin)
        if statut:
            query = query.filter(FeuilleTacheModel.statut_validation == statut.value)

        models = (
            query.order_by(FeuilleTacheModel.date_travail.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [m.to_entity() for m in models]

    def find_en_attente_validation(
        self,
        chantier_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[FeuilleTache]:
        """Trouve les feuilles en attente de validation (TAC-19)."""
        query = self.session.query(FeuilleTacheModel).filter(
            FeuilleTacheModel.statut_validation == StatutValidation.EN_ATTENTE.value
        )

        if chantier_id:
            query = query.filter(FeuilleTacheModel.chantier_id == chantier_id)

        models = (
            query.order_by(FeuilleTacheModel.date_travail.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [m.to_entity() for m in models]

    def save(self, feuille: FeuilleTache) -> FeuilleTache:
        """Persiste une feuille."""
        if feuille.id:
            # Mise a jour
            model = (
                self.session.query(FeuilleTacheModel)
                .filter(FeuilleTacheModel.id == feuille.id)
                .first()
            )
            if model:
                model.heures_travaillees = feuille.heures_travaillees
                model.quantite_realisee = feuille.quantite_realisee
                model.commentaire = feuille.commentaire
                model.statut_validation = feuille.statut_validation.value
                model.validateur_id = feuille.validateur_id
                model.date_validation = feuille.date_validation
                model.motif_rejet = feuille.motif_rejet
                model.updated_at = feuille.updated_at
        else:
            # Creation
            model = FeuilleTacheModel.from_entity(feuille)
            self.session.add(model)

        self.session.commit()
        self.session.refresh(model)
        return model.to_entity()

    def delete(self, feuille_id: int) -> bool:
        """Supprime une feuille."""
        model = (
            self.session.query(FeuilleTacheModel)
            .filter(FeuilleTacheModel.id == feuille_id)
            .first()
        )
        if not model:
            return False

        self.session.delete(model)
        self.session.commit()
        return True

    def count_by_tache(self, tache_id: int) -> int:
        """Compte les feuilles d'une tache."""
        return (
            self.session.query(func.count(FeuilleTacheModel.id))
            .filter(FeuilleTacheModel.tache_id == tache_id)
            .scalar()
        )

    def get_total_heures_tache(self, tache_id: int, validees_only: bool = True) -> float:
        """Calcule le total des heures pour une tache."""
        query = self.session.query(func.sum(FeuilleTacheModel.heures_travaillees)).filter(
            FeuilleTacheModel.tache_id == tache_id
        )

        if validees_only:
            query = query.filter(
                FeuilleTacheModel.statut_validation == StatutValidation.VALIDEE.value
            )

        result = query.scalar()
        return result or 0.0

    def get_total_quantite_tache(self, tache_id: int, validees_only: bool = True) -> float:
        """Calcule le total des quantites pour une tache."""
        query = self.session.query(func.sum(FeuilleTacheModel.quantite_realisee)).filter(
            FeuilleTacheModel.tache_id == tache_id
        )

        if validees_only:
            query = query.filter(
                FeuilleTacheModel.statut_validation == StatutValidation.VALIDEE.value
            )

        result = query.scalar()
        return result or 0.0

    def exists_for_date(
        self,
        tache_id: int,
        utilisateur_id: int,
        date_travail: date,
    ) -> bool:
        """Verifie si une feuille existe pour cette combinaison."""
        return (
            self.session.query(FeuilleTacheModel)
            .filter(FeuilleTacheModel.tache_id == tache_id)
            .filter(FeuilleTacheModel.utilisateur_id == utilisateur_id)
            .filter(FeuilleTacheModel.date_travail == date_travail)
            .first()
            is not None
        )
