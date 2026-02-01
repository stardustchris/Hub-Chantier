"""Interface du repository pour les lots de devis.

DEV-03: Creation devis structure - CRUD des lots/chapitres.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities import LotDevis


class LotDevisRepository(ABC):
    """Interface abstraite pour la persistence des lots de devis."""

    @abstractmethod
    def save(self, lot: LotDevis) -> LotDevis:
        """Persiste un lot de devis (creation ou mise a jour).

        Args:
            lot: Le lot a persister.

        Returns:
            Le lot avec son ID attribue.
        """
        pass

    @abstractmethod
    def find_by_id(self, lot_id: int) -> Optional[LotDevis]:
        """Recherche un lot par son ID.

        Args:
            lot_id: L'ID du lot.

        Returns:
            Le lot ou None si non trouve.
        """
        pass

    @abstractmethod
    def find_by_devis(
        self,
        devis_id: int,
        parent_id: Optional[int] = None,
    ) -> List[LotDevis]:
        """Liste les lots d'un devis, optionnellement filtres par parent.

        Args:
            devis_id: L'ID du devis.
            parent_id: Filtrer par lot parent (None = lots racine).

        Returns:
            Liste des lots ordonnee par le champ ordre.
        """
        pass

    @abstractmethod
    def find_children(self, parent_id: int) -> List[LotDevis]:
        """Liste les sous-chapitres d'un lot.

        Args:
            parent_id: L'ID du lot parent.

        Returns:
            Liste des sous-chapitres ordonnee par le champ ordre.
        """
        pass

    @abstractmethod
    def count_by_devis(self, devis_id: int) -> int:
        """Compte le nombre de lots d'un devis.

        Args:
            devis_id: L'ID du devis.

        Returns:
            Le nombre de lots.
        """
        pass

    @abstractmethod
    def delete(self, lot_id: int, deleted_by: Optional[int] = None) -> bool:
        """Supprime un lot (soft delete - H10).

        Args:
            lot_id: L'ID du lot a supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.

        Returns:
            True si supprime, False si non trouve.
        """
        pass
