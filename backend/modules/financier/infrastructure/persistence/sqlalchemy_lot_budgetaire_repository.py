"""Implementation SQLAlchemy du repository LotBudgetaire.

FIN-02: Decomposition en lots - CRUD des lots budgetaires.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from ...domain.entities import LotBudgetaire
from ...domain.repositories import LotBudgetaireRepository
from ...domain.value_objects import UniteMesure
from .models import LotBudgetaireModel


class SQLAlchemyLotBudgetaireRepository(LotBudgetaireRepository):
    """Implementation SQLAlchemy du repository LotBudgetaire."""

    def __init__(self, session: Session):
        """Initialise le repository avec une session SQLAlchemy.

        Args:
            session: La session SQLAlchemy.
        """
        self._session = session

    def _to_entity(self, model: LotBudgetaireModel) -> LotBudgetaire:
        """Convertit un modele SQLAlchemy en entite domain.

        Args:
            model: Le modele SQLAlchemy source.

        Returns:
            L'entite LotBudgetaire correspondante.
        """
        return LotBudgetaire(
            id=model.id,
            budget_id=model.budget_id,
            code_lot=model.code_lot,
            libelle=model.libelle,
            unite=UniteMesure(model.unite) if model.unite else UniteMesure.U,
            quantite_prevue=Decimal(str(model.quantite_prevue)),
            prix_unitaire_ht=Decimal(str(model.prix_unitaire_ht)),
            parent_lot_id=model.parent_lot_id,
            ordre=model.ordre,
            created_at=model.created_at,
            updated_at=model.updated_at,
            created_by=model.created_by,
            deleted_at=model.deleted_at,
            deleted_by=model.deleted_by,
        )

    def _to_model(self, entity: LotBudgetaire) -> LotBudgetaireModel:
        """Convertit une entite domain en modele SQLAlchemy.

        Args:
            entity: L'entite LotBudgetaire source.

        Returns:
            Le modele SQLAlchemy correspondant.
        """
        return LotBudgetaireModel(
            id=entity.id,
            budget_id=entity.budget_id,
            code_lot=entity.code_lot,
            libelle=entity.libelle,
            unite=entity.unite.value,
            quantite_prevue=entity.quantite_prevue,
            prix_unitaire_ht=entity.prix_unitaire_ht,
            parent_lot_id=entity.parent_lot_id,
            ordre=entity.ordre,
            created_at=entity.created_at or datetime.utcnow(),
            updated_at=entity.updated_at,
            created_by=entity.created_by,
        )

    def save(self, lot: LotBudgetaire) -> LotBudgetaire:
        """Persiste un lot budgetaire (creation ou mise a jour).

        Args:
            lot: Le lot a persister.

        Returns:
            Le lot avec son ID attribue.
        """
        if lot.id:
            # Mise a jour
            model = (
                self._session.query(LotBudgetaireModel)
                .filter(LotBudgetaireModel.id == lot.id)
                .first()
            )
            if model:
                model.code_lot = lot.code_lot
                model.libelle = lot.libelle
                model.unite = lot.unite.value
                model.quantite_prevue = lot.quantite_prevue
                model.prix_unitaire_ht = lot.prix_unitaire_ht
                model.parent_lot_id = lot.parent_lot_id
                model.ordre = lot.ordre
                model.updated_at = datetime.utcnow()
        else:
            # Creation
            model = self._to_model(lot)
            self._session.add(model)

        self._session.flush()
        return self._to_entity(model)

    def find_by_id(self, lot_id: int) -> Optional[LotBudgetaire]:
        """Recherche un lot par son ID (exclut les supprimes).

        Args:
            lot_id: L'ID du lot.

        Returns:
            Le lot ou None si non trouve.
        """
        model = (
            self._session.query(LotBudgetaireModel)
            .filter(LotBudgetaireModel.id == lot_id)
            .filter(LotBudgetaireModel.deleted_at.is_(None))
            .first()
        )
        return self._to_entity(model) if model else None

    def find_by_budget_id(self, budget_id: int) -> List[LotBudgetaire]:
        """Liste tous les lots d'un budget (exclut les supprimes).

        Args:
            budget_id: L'ID du budget.

        Returns:
            Liste des lots du budget.
        """
        query = (
            self._session.query(LotBudgetaireModel)
            .filter(LotBudgetaireModel.budget_id == budget_id)
            .filter(LotBudgetaireModel.deleted_at.is_(None))
            .order_by(LotBudgetaireModel.ordre, LotBudgetaireModel.code_lot)
        )
        return [self._to_entity(model) for model in query.all()]

    def find_by_code(self, budget_id: int, code_lot: str) -> Optional[LotBudgetaire]:
        """Recherche un lot par son code dans un budget (exclut les supprimes).

        Args:
            budget_id: L'ID du budget.
            code_lot: Le code du lot.

        Returns:
            Le lot ou None si non trouve.
        """
        model = (
            self._session.query(LotBudgetaireModel)
            .filter(LotBudgetaireModel.budget_id == budget_id)
            .filter(LotBudgetaireModel.code_lot == code_lot)
            .filter(LotBudgetaireModel.deleted_at.is_(None))
            .first()
        )
        return self._to_entity(model) if model else None

    def find_all_by_budget(
        self,
        budget_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> List[LotBudgetaire]:
        """Liste les lots d'un budget avec pagination (exclut les supprimes).

        Args:
            budget_id: L'ID du budget.
            limit: Nombre maximum de resultats.
            offset: Decalage pour pagination.

        Returns:
            Liste des lots.
        """
        query = (
            self._session.query(LotBudgetaireModel)
            .filter(LotBudgetaireModel.budget_id == budget_id)
            .filter(LotBudgetaireModel.deleted_at.is_(None))
            .order_by(LotBudgetaireModel.ordre, LotBudgetaireModel.code_lot)
            .offset(offset)
            .limit(limit)
        )
        return [self._to_entity(model) for model in query.all()]

    def count_by_budget(self, budget_id: int) -> int:
        """Compte le nombre de lots d'un budget (exclut les supprimes).

        Args:
            budget_id: L'ID du budget.

        Returns:
            Le nombre de lots.
        """
        return (
            self._session.query(LotBudgetaireModel)
            .filter(LotBudgetaireModel.budget_id == budget_id)
            .filter(LotBudgetaireModel.deleted_at.is_(None))
            .count()
        )

    def delete(self, lot_id: int, deleted_by: Optional[int] = None) -> bool:
        """Supprime un lot (soft delete - H10).

        Args:
            lot_id: L'ID du lot a supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.

        Returns:
            True si supprime, False si non trouve.
        """
        model = (
            self._session.query(LotBudgetaireModel)
            .filter(LotBudgetaireModel.id == lot_id)
            .filter(LotBudgetaireModel.deleted_at.is_(None))
            .first()
        )
        if not model:
            return False

        model.deleted_at = datetime.utcnow()
        model.deleted_by = deleted_by
        self._session.flush()
        return True
