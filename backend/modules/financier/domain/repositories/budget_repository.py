"""Interface du repository pour les budgets.

FIN-01: Budget prévisionnel - CRUD des budgets par chantier.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities import Budget


class BudgetRepository(ABC):
    """Interface abstraite pour la persistence des budgets."""

    @abstractmethod
    def save(self, budget: Budget) -> Budget:
        """Persiste un budget (création ou mise à jour).

        Args:
            budget: Le budget à persister.

        Returns:
            Le budget avec son ID attribué.
        """
        pass

    @abstractmethod
    def find_by_id(self, budget_id: int) -> Optional[Budget]:
        """Recherche un budget par son ID.

        Args:
            budget_id: L'ID du budget.

        Returns:
            Le budget ou None si non trouvé.
        """
        pass

    @abstractmethod
    def find_by_chantier_id(self, chantier_id: int) -> Optional[Budget]:
        """Recherche le budget d'un chantier.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Le budget du chantier ou None si non trouvé.
        """
        pass

    @abstractmethod
    def find_all(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Budget]:
        """Liste tous les budgets.

        Args:
            limit: Nombre maximum de résultats.
            offset: Décalage pour pagination.

        Returns:
            Liste des budgets.
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """Compte le nombre de budgets.

        Returns:
            Le nombre de budgets.
        """
        pass

    @abstractmethod
    def delete(self, budget_id: int, deleted_by: Optional[int] = None) -> bool:
        """Supprime un budget (soft delete - H10).

        Args:
            budget_id: L'ID du budget à supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.

        Returns:
            True si supprimé, False si non trouvé.
        """
        pass
