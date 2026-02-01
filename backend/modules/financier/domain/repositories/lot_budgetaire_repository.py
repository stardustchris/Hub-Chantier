"""Interface du repository pour les lots budgétaires.

FIN-02: Décomposition en lots - CRUD des lots budgétaires.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities import LotBudgetaire


class LotBudgetaireRepository(ABC):
    """Interface abstraite pour la persistence des lots budgétaires."""

    @abstractmethod
    def save(self, lot: LotBudgetaire) -> LotBudgetaire:
        """Persiste un lot budgétaire (création ou mise à jour).

        Args:
            lot: Le lot à persister.

        Returns:
            Le lot avec son ID attribué.
        """
        pass

    @abstractmethod
    def find_by_id(self, lot_id: int) -> Optional[LotBudgetaire]:
        """Recherche un lot par son ID.

        Args:
            lot_id: L'ID du lot.

        Returns:
            Le lot ou None si non trouvé.
        """
        pass

    @abstractmethod
    def find_by_budget_id(self, budget_id: int) -> List[LotBudgetaire]:
        """Liste tous les lots d'un budget.

        Args:
            budget_id: L'ID du budget.

        Returns:
            Liste des lots du budget.
        """
        pass

    @abstractmethod
    def find_by_code(self, budget_id: int, code_lot: str) -> Optional[LotBudgetaire]:
        """Recherche un lot par son code dans un budget.

        Args:
            budget_id: L'ID du budget.
            code_lot: Le code du lot.

        Returns:
            Le lot ou None si non trouvé.
        """
        pass

    @abstractmethod
    def find_all_by_budget(
        self,
        budget_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> List[LotBudgetaire]:
        """Liste les lots d'un budget avec pagination.

        Args:
            budget_id: L'ID du budget.
            limit: Nombre maximum de résultats.
            offset: Décalage pour pagination.

        Returns:
            Liste des lots.
        """
        pass

    @abstractmethod
    def count_by_budget(self, budget_id: int) -> int:
        """Compte le nombre de lots d'un budget.

        Args:
            budget_id: L'ID du budget.

        Returns:
            Le nombre de lots.
        """
        pass

    @abstractmethod
    def find_by_devis_id(self, devis_id: UUID) -> List[LotBudgetaire]:
        """Liste tous les lots d'un devis.

        Args:
            devis_id: L'UUID du devis.

        Returns:
            Liste des lots du devis, triés par ordre et code.
        """
        pass

    @abstractmethod
    def count_by_devis_id(self, devis_id: UUID) -> int:
        """Compte le nombre de lots d'un devis.

        Args:
            devis_id: L'UUID du devis.

        Returns:
            Le nombre de lots.
        """
        pass

    @abstractmethod
    def delete(self, lot_id: int, deleted_by: Optional[int] = None) -> bool:
        """Supprime un lot (soft delete - H10).

        Args:
            lot_id: L'ID du lot à supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.

        Returns:
            True si supprimé, False si non trouvé.
        """
        pass
