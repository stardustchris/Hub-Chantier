"""Interface du repository pour les affectations taches <-> lots budgetaires.

FIN-03: Affectation budgets aux taches.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.affectation_tache_lot import AffectationTacheLot


class AffectationRepository(ABC):
    """Interface abstraite pour la persistence des affectations taches/lots."""

    @abstractmethod
    def save(self, affectation: AffectationTacheLot) -> AffectationTacheLot:
        """Persiste une affectation (creation ou mise a jour).

        Args:
            affectation: L'affectation a persister.

        Returns:
            L'affectation avec son ID attribue.
        """
        pass

    @abstractmethod
    def find_by_id(self, affectation_id: int) -> Optional[AffectationTacheLot]:
        """Recherche une affectation par son ID.

        Args:
            affectation_id: L'ID de l'affectation.

        Returns:
            L'affectation ou None si non trouvee.
        """
        pass

    @abstractmethod
    def find_by_tache(self, tache_id: int) -> List[AffectationTacheLot]:
        """Recherche les affectations d'une tache.

        Args:
            tache_id: L'ID de la tache.

        Returns:
            Liste des affectations de la tache.
        """
        pass

    @abstractmethod
    def find_by_lot(self, lot_budgetaire_id: int) -> List[AffectationTacheLot]:
        """Recherche les affectations d'un lot budgetaire.

        Args:
            lot_budgetaire_id: L'ID du lot budgetaire.

        Returns:
            Liste des affectations du lot.
        """
        pass

    @abstractmethod
    def find_by_chantier(self, chantier_id: int) -> List[AffectationTacheLot]:
        """Recherche les affectations d'un chantier.

        Args:
            chantier_id: L'ID du chantier.

        Returns:
            Liste des affectations du chantier.
        """
        pass

    @abstractmethod
    def delete(self, affectation_id: int) -> bool:
        """Supprime une affectation (hard delete - table de liaison).

        Args:
            affectation_id: L'ID de l'affectation a supprimer.

        Returns:
            True si supprimee, False si non trouvee.
        """
        pass

    @abstractmethod
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
        pass
