"""Interface du repository pour les comparatifs de devis.

DEV-08: Variantes et revisions - Persistance des comparatifs.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.comparatif_devis import ComparatifDevis


class ComparatifRepository(ABC):
    """Interface abstraite pour la persistence des comparatifs de devis."""

    @abstractmethod
    def save(self, comparatif: ComparatifDevis) -> ComparatifDevis:
        """Persiste un comparatif (creation ou mise a jour).

        Persiste aussi les lignes du comparatif (cascade).

        Args:
            comparatif: Le comparatif a persister.

        Returns:
            Le comparatif avec son ID attribue.
        """
        pass

    @abstractmethod
    def find_by_id(self, comparatif_id: int) -> Optional[ComparatifDevis]:
        """Recherche un comparatif par son ID.

        Args:
            comparatif_id: L'ID du comparatif.

        Returns:
            Le comparatif avec ses lignes ou None si non trouve.
        """
        pass

    @abstractmethod
    def find_by_devis(self, devis_id: int) -> List[ComparatifDevis]:
        """Liste les comparatifs impliquant un devis (source ou cible).

        Args:
            devis_id: L'ID du devis.

        Returns:
            Liste des comparatifs (sans les lignes pour performance).
        """
        pass

    @abstractmethod
    def find_by_pair(
        self, devis_source_id: int, devis_cible_id: int
    ) -> Optional[ComparatifDevis]:
        """Recherche un comparatif existant entre deux devis.

        Args:
            devis_source_id: L'ID du devis source.
            devis_cible_id: L'ID du devis cible.

        Returns:
            Le comparatif avec ses lignes ou None si non trouve.
        """
        pass
