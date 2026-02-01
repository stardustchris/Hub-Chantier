"""Interface du repository pour les affectations budget-tache.

FIN-03: Affectation budgets aux taches - CRUD et recherche.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.affectation_budget_tache import AffectationBudgetTache


class AffectationBudgetTacheRepository(ABC):
    """Interface abstraite pour la persistence des affectations budget-tache.

    Note:
        Le Domain ne connait pas l'implementation concrete.
    """

    @abstractmethod
    def find_by_id(self, affectation_id: int) -> Optional[AffectationBudgetTache]:
        """Recherche une affectation par son ID.

        Args:
            affectation_id: L'ID de l'affectation.

        Returns:
            L'affectation ou None si non trouvee.
        """
        pass

    @abstractmethod
    def find_by_lot(self, lot_budgetaire_id: int) -> List[AffectationBudgetTache]:
        """Liste les affectations d'un lot budgetaire.

        Args:
            lot_budgetaire_id: L'ID du lot budgetaire.

        Returns:
            Liste des affectations du lot.
        """
        pass

    @abstractmethod
    def find_by_tache(self, tache_id: int) -> List[AffectationBudgetTache]:
        """Liste les affectations d'une tache.

        Args:
            tache_id: L'ID de la tache.

        Returns:
            Liste des affectations de la tache.
        """
        pass

    @abstractmethod
    def find_by_chantier(self, chantier_id: int) -> List[AffectationBudgetTache]:
        """Liste les affectations d'un chantier (via les lots du budget).

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Liste des affectations du chantier.
        """
        pass

    @abstractmethod
    def save(self, affectation: AffectationBudgetTache) -> AffectationBudgetTache:
        """Persiste une affectation (creation ou mise a jour).

        Args:
            affectation: L'affectation a persister.

        Returns:
            L'affectation avec son ID attribue.
        """
        pass

    @abstractmethod
    def delete(self, affectation_id: int) -> None:
        """Supprime une affectation.

        Args:
            affectation_id: L'ID de l'affectation a supprimer.
        """
        pass
