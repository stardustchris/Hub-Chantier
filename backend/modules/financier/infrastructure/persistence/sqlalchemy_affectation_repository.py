"""Implementation SQLAlchemy du repository Affectation.

FIN-03: Affectation budgets aux taches - CRUD des affectations taches/lots.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from ...domain.entities.affectation_tache_lot import AffectationTacheLot
from ...domain.repositories.affectation_repository import AffectationRepository
from .models import AffectationTacheLotModel


class SQLAlchemyAffectationRepository(AffectationRepository):
    """Implementation SQLAlchemy du repository Affectation."""

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def _to_entity(self, model: AffectationTacheLotModel) -> AffectationTacheLot:
        """Convertit un modele SQLAlchemy en entite domain.

        Args:
            model: Le modele SQLAlchemy source.

        Returns:
            L'entite AffectationTacheLot correspondante.
        """
        return AffectationTacheLot(
            id=model.id,
            chantier_id=model.chantier_id,
            tache_id=model.tache_id,
            lot_budgetaire_id=model.lot_budgetaire_id,
            pourcentage_affectation=Decimal(str(model.pourcentage_affectation)),
            created_at=model.created_at,
            created_by=model.created_by,
        )

    def save(self, affectation: AffectationTacheLot) -> AffectationTacheLot:
        """Persiste une affectation (creation uniquement pour table de liaison).

        Args:
            affectation: L'affectation a persister.

        Returns:
            L'affectation avec son ID attribue.
        """
        if affectation.id:
            # Mise a jour (rare pour table de liaison)
            model = (
                self._session.query(AffectationTacheLotModel)
                .filter(AffectationTacheLotModel.id == affectation.id)
                .first()
            )
            if model:
                model.pourcentage_affectation = affectation.pourcentage_affectation
        else:
            # Creation
            model = AffectationTacheLotModel(
                chantier_id=affectation.chantier_id,
                tache_id=affectation.tache_id,
                lot_budgetaire_id=affectation.lot_budgetaire_id,
                pourcentage_affectation=affectation.pourcentage_affectation,
                created_at=affectation.created_at or datetime.utcnow(),
                created_by=affectation.created_by,
            )
            self._session.add(model)

        self._session.flush()
        return self._to_entity(model)

    def find_by_id(self, affectation_id: int) -> Optional[AffectationTacheLot]:
        """Recherche une affectation par son ID.

        Args:
            affectation_id: L'ID de l'affectation.

        Returns:
            L'affectation ou None si non trouvee.
        """
        model = (
            self._session.query(AffectationTacheLotModel)
            .filter(AffectationTacheLotModel.id == affectation_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_tache(self, tache_id: int) -> List[AffectationTacheLot]:
        """Recherche les affectations d'une tache.

        Args:
            tache_id: L'ID de la tache.

        Returns:
            Liste des affectations de la tache.
        """
        models = (
            self._session.query(AffectationTacheLotModel)
            .filter(AffectationTacheLotModel.tache_id == tache_id)
            .order_by(AffectationTacheLotModel.id)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_by_lot(self, lot_budgetaire_id: int) -> List[AffectationTacheLot]:
        """Recherche les affectations d'un lot budgetaire.

        Args:
            lot_budgetaire_id: L'ID du lot budgetaire.

        Returns:
            Liste des affectations du lot.
        """
        models = (
            self._session.query(AffectationTacheLotModel)
            .filter(AffectationTacheLotModel.lot_budgetaire_id == lot_budgetaire_id)
            .order_by(AffectationTacheLotModel.id)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def find_by_chantier(self, chantier_id: int) -> List[AffectationTacheLot]:
        """Recherche les affectations d'un chantier.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Liste des affectations du chantier.
        """
        models = (
            self._session.query(AffectationTacheLotModel)
            .filter(AffectationTacheLotModel.chantier_id == chantier_id)
            .order_by(AffectationTacheLotModel.id)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def delete(self, affectation_id: int) -> bool:
        """Supprime une affectation (hard delete - table de liaison).

        Args:
            affectation_id: L'ID de l'affectation a supprimer.

        Returns:
            True si supprimee, False si non trouvee.
        """
        model = (
            self._session.query(AffectationTacheLotModel)
            .filter(AffectationTacheLotModel.id == affectation_id)
            .first()
        )
        if not model:
            return False

        self._session.delete(model)
        self._session.flush()
        return True

    def find_by_tache_and_lot(
        self, tache_id: int, lot_id: int
    ) -> Optional[AffectationTacheLot]:
        """Recherche une affectation par tache et lot (unicite).

        Args:
            tache_id: L'ID de la tache.
            lot_id: L'ID du lot budgetaire.

        Returns:
            L'affectation ou None si non trouvee.
        """
        model = (
            self._session.query(AffectationTacheLotModel)
            .filter(AffectationTacheLotModel.tache_id == tache_id)
            .filter(AffectationTacheLotModel.lot_budgetaire_id == lot_id)
            .first()
        )
        return self._to_entity(model) if model else None
