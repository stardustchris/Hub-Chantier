"""Implementation SQLAlchemy du repository Budget.

FIN-01: Budget previsionnel - CRUD des budgets par chantier.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from ...domain.entities import Budget
from ...domain.repositories import BudgetRepository
from .models import BudgetModel


class SQLAlchemyBudgetRepository(BudgetRepository):
    """Implementation SQLAlchemy du repository Budget."""

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def _to_entity(self, model: BudgetModel) -> Budget:
        """Convertit un modele SQLAlchemy en entite domain.

        Args:
            model: Le modele SQLAlchemy source.

        Returns:
            L'entite Budget correspondante.
        """
        return Budget(
            id=model.id,
            chantier_id=model.chantier_id,
            montant_initial_ht=Decimal(str(model.montant_initial_ht)),
            montant_avenants_ht=Decimal(str(model.montant_avenants_ht)),
            retenue_garantie_pct=Decimal(str(model.retenue_garantie_pct)),
            seuil_alerte_pct=Decimal(str(model.seuil_alerte_pct)),
            seuil_validation_achat=Decimal(str(model.seuil_validation_achat)),
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            deleted_at=model.deleted_at,
            deleted_by=model.deleted_by,
        )

    def _to_model(self, entity: Budget) -> BudgetModel:
        """Convertit une entite domain en modele SQLAlchemy.

        Args:
            entity: L'entite Budget source.

        Returns:
            Le modele SQLAlchemy correspondant.
        """
        return BudgetModel(
            id=entity.id,
            chantier_id=entity.chantier_id,
            montant_initial_ht=entity.montant_initial_ht,
            montant_avenants_ht=entity.montant_avenants_ht,
            retenue_garantie_pct=entity.retenue_garantie_pct,
            seuil_alerte_pct=entity.seuil_alerte_pct,
            seuil_validation_achat=entity.seuil_validation_achat,
            notes=entity.notes,
            created_at=entity.created_at or datetime.utcnow(),
            updated_at=entity.updated_at,
            created_by=entity.created_by,
        )

    def save(self, budget: Budget) -> Budget:
        """Persiste un budget (creation ou mise a jour).

        Args:
            budget: Le budget a persister.

        Returns:
            Le budget avec son ID attribue.
        """
        if budget.id:
            # Mise a jour
            model = (
                self._session.query(BudgetModel)
                .filter(BudgetModel.id == budget.id)
                .first()
            )
            if model:
                model.montant_initial_ht = budget.montant_initial_ht
                model.montant_avenants_ht = budget.montant_avenants_ht
                model.retenue_garantie_pct = budget.retenue_garantie_pct
                model.seuil_alerte_pct = budget.seuil_alerte_pct
                model.seuil_validation_achat = budget.seuil_validation_achat
                model.notes = budget.notes
                model.updated_at = datetime.utcnow()
        else:
            # Creation
            model = self._to_model(budget)
            self._session.add(model)

        self._session.flush()
        return self._to_entity(model)

    def find_by_id(self, budget_id: int) -> Optional[Budget]:
        """Recherche un budget par son ID (exclut les supprimes).

        Args:
            budget_id: L'ID du budget.

        Returns:
            Le budget ou None si non trouve.
        """
        model = (
            self._session.query(BudgetModel)
            .filter(BudgetModel.id == budget_id)
            .filter(BudgetModel.deleted_at.is_(None))
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_chantier_id(self, chantier_id: int) -> Optional[Budget]:
        """Recherche le budget d'un chantier (exclut les supprimes).

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Le budget du chantier ou None si non trouve.
        """
        model = (
            self._session.query(BudgetModel)
            .filter(BudgetModel.chantier_id == chantier_id)
            .filter(BudgetModel.deleted_at.is_(None))
            .first()
        )
        return self._to_entity(model) if model else None

    def find_all(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Budget]:
        """Liste tous les budgets (exclut les supprimes).

        Args:
            limit: Nombre maximum de resultats.
            offset: Decalage pour pagination.

        Returns:
            Liste des budgets.
        """
        query = self._session.query(BudgetModel)
        query = query.filter(BudgetModel.deleted_at.is_(None))
        query = query.order_by(BudgetModel.chantier_id)
        query = query.offset(offset).limit(limit)

        return [self._to_entity(model) for model in query.all()]

    def count(self) -> int:
        """Compte le nombre de budgets (exclut les supprimes).

        Returns:
            Le nombre de budgets.
        """
        return (
            self._session.query(BudgetModel)
            .filter(BudgetModel.deleted_at.is_(None))
            .count()
        )

    def delete(self, budget_id: int, deleted_by: Optional[int] = None) -> bool:
        """Supprime un budget (soft delete - H10).

        Args:
            budget_id: L'ID du budget a supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.

        Returns:
            True si supprime, False si non trouve.
        """
        model = (
            self._session.query(BudgetModel)
            .filter(BudgetModel.id == budget_id)
            .filter(BudgetModel.deleted_at.is_(None))
            .first()
        )
        if not model:
            return False

        model.deleted_at = datetime.utcnow()
        model.deleted_by = deleted_by
        self._session.flush()
        return True
