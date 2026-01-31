"""Interface du repository pour les avenants budgétaires.

FIN-04: Avenants budgétaires - CRUD et somme des avenants validés.
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List, Optional

from ..entities.avenant_budgetaire import AvenantBudgetaire


class AvenantRepository(ABC):
    """Interface abstraite pour la persistence des avenants budgétaires."""

    @abstractmethod
    def save(self, avenant: AvenantBudgetaire) -> AvenantBudgetaire:
        """Persiste un avenant (création ou mise à jour).

        Args:
            avenant: L'avenant à persister.

        Returns:
            L'avenant avec son ID attribué.
        """
        pass

    @abstractmethod
    def find_by_id(self, avenant_id: int) -> Optional[AvenantBudgetaire]:
        """Recherche un avenant par son ID.

        Args:
            avenant_id: L'ID de l'avenant.

        Returns:
            L'avenant ou None si non trouvé.
        """
        pass

    @abstractmethod
    def find_by_budget_id(
        self, budget_id: int, include_deleted: bool = False
    ) -> List[AvenantBudgetaire]:
        """Liste les avenants d'un budget.

        Args:
            budget_id: L'ID du budget.
            include_deleted: Inclure les avenants supprimés.

        Returns:
            Liste des avenants du budget.
        """
        pass

    @abstractmethod
    def count_by_budget_id(self, budget_id: int) -> int:
        """Compte le nombre d'avenants pour un budget (non supprimés).

        Args:
            budget_id: L'ID du budget.

        Returns:
            Le nombre d'avenants.
        """
        pass

    @abstractmethod
    def delete(self, avenant_id: int, deleted_by: int) -> None:
        """Supprime un avenant (soft delete - H10).

        Args:
            avenant_id: L'ID de l'avenant à supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.
        """
        pass

    @abstractmethod
    def somme_avenants_valides(self, budget_id: int) -> Decimal:
        """Calcule la somme des montants HT des avenants validés d'un budget.

        Args:
            budget_id: L'ID du budget.

        Returns:
            La somme des montants HT des avenants validés.
        """
        pass
