"""Implementation SQLAlchemy du repository AffectationBudgetTache.

FIN-03: Affectation budgets aux taches - CRUD et recherche.
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from ...domain.entities.affectation_budget_tache import AffectationBudgetTache
from ...domain.repositories.affectation_repository import AffectationBudgetTacheRepository
from .models import AffectationBudgetTacheModel, BudgetModel, LotBudgetaireModel

logger = logging.getLogger(__name__)


class SQLAlchemyAffectationBudgetTacheRepository(AffectationBudgetTacheRepository):
    """Implementation SQLAlchemy du repository AffectationBudgetTache."""

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def _to_entity(self, model: AffectationBudgetTacheModel) -> AffectationBudgetTache:
        """Convertit un modele SQLAlchemy en entite domain.

        Args:
            model: Le modele SQLAlchemy source.

        Returns:
            L'entite AffectationBudgetTache correspondante.
        """
        return AffectationBudgetTache(
            id=model.id,
            lot_budgetaire_id=model.lot_budgetaire_id,
            tache_id=model.tache_id,
            pourcentage_allocation=Decimal(str(model.pourcentage_allocation)),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: AffectationBudgetTache) -> AffectationBudgetTacheModel:
        """Convertit une entite domain en modele SQLAlchemy.

        Args:
            entity: L'entite AffectationBudgetTache source.

        Returns:
            Le modele SQLAlchemy correspondant.
        """
        return AffectationBudgetTacheModel(
            id=entity.id,
            lot_budgetaire_id=entity.lot_budgetaire_id,
            tache_id=entity.tache_id,
            pourcentage_allocation=entity.pourcentage_allocation,
            created_at=entity.created_at or datetime.utcnow(),
        )

    def find_by_id(self, affectation_id: int) -> Optional[AffectationBudgetTache]:
        """Recherche une affectation par son ID.

        Args:
            affectation_id: L'ID de l'affectation.

        Returns:
            L'affectation ou None si non trouvee.
        """
        model = (
            self._session.query(AffectationBudgetTacheModel)
            .filter(AffectationBudgetTacheModel.id == affectation_id)
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_lot(self, lot_budgetaire_id: int) -> List[AffectationBudgetTache]:
        """Liste les affectations d'un lot budgetaire.

        Args:
            lot_budgetaire_id: L'ID du lot budgetaire.

        Returns:
            Liste des affectations du lot.
        """
        query = (
            self._session.query(AffectationBudgetTacheModel)
            .filter(AffectationBudgetTacheModel.lot_budgetaire_id == lot_budgetaire_id)
            .order_by(AffectationBudgetTacheModel.created_at.asc())
        )
        return [self._to_entity(model) for model in query.all()]

    def find_by_tache(self, tache_id: int) -> List[AffectationBudgetTache]:
        """Liste les affectations d'une tache.

        Args:
            tache_id: L'ID de la tache.

        Returns:
            Liste des affectations de la tache.
        """
        query = (
            self._session.query(AffectationBudgetTacheModel)
            .filter(AffectationBudgetTacheModel.tache_id == tache_id)
            .order_by(AffectationBudgetTacheModel.created_at.asc())
        )
        return [self._to_entity(model) for model in query.all()]

    def find_by_chantier(self, chantier_id: int) -> List[AffectationBudgetTache]:
        """Liste les affectations d'un chantier (via les lots du budget).

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Liste des affectations du chantier.
        """
        query = (
            self._session.query(AffectationBudgetTacheModel)
            .join(
                LotBudgetaireModel,
                AffectationBudgetTacheModel.lot_budgetaire_id == LotBudgetaireModel.id,
            )
            .join(
                BudgetModel,
                LotBudgetaireModel.budget_id == BudgetModel.id,
            )
            .filter(BudgetModel.chantier_id == chantier_id)
            .filter(LotBudgetaireModel.deleted_at.is_(None))
            .filter(BudgetModel.deleted_at.is_(None))
            .order_by(AffectationBudgetTacheModel.created_at.asc())
        )
        return [self._to_entity(model) for model in query.all()]

    def save(self, affectation: AffectationBudgetTache) -> AffectationBudgetTache:
        """Persiste une affectation (creation ou mise a jour).

        Args:
            affectation: L'affectation a persister.

        Returns:
            L'affectation avec son ID attribue.
        """
        if affectation.id:
            # Mise a jour
            model = (
                self._session.query(AffectationBudgetTacheModel)
                .filter(AffectationBudgetTacheModel.id == affectation.id)
                .first()
            )
            if model:
                model.lot_budgetaire_id = affectation.lot_budgetaire_id
                model.tache_id = affectation.tache_id
                model.pourcentage_allocation = affectation.pourcentage_allocation
                model.updated_at = datetime.utcnow()
        else:
            # Creation
            model = self._to_model(affectation)
            self._session.add(model)

        self._session.flush()
        logger.info(
            "Affectation budget-tache sauvegardee: id=%s lot=%s tache=%s pct=%s",
            model.id, model.lot_budgetaire_id, model.tache_id,
            model.pourcentage_allocation,
        )
        return self._to_entity(model)

    def delete(self, affectation_id: int) -> None:
        """Supprime une affectation.

        Args:
            affectation_id: L'ID de l'affectation a supprimer.
        """
        model = (
            self._session.query(AffectationBudgetTacheModel)
            .filter(AffectationBudgetTacheModel.id == affectation_id)
            .first()
        )
        if model:
            self._session.delete(model)
            self._session.flush()
            logger.info("Affectation budget-tache supprimee: id=%s", affectation_id)
