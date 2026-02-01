"""Interface du repository pour les lignes de devis.

DEV-03: Creation devis structure - CRUD des lignes dans les lots.
"""

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import List, Optional

from ..entities import LigneDevis


class LigneDevisRepository(ABC):
    """Interface abstraite pour la persistence des lignes de devis."""

    @abstractmethod
    def save(self, ligne: LigneDevis) -> LigneDevis:
        """Persiste une ligne de devis (creation ou mise a jour).

        Args:
            ligne: La ligne a persister.

        Returns:
            La ligne avec son ID attribue.
        """
        pass

    @abstractmethod
    def find_by_id(self, ligne_id: int) -> Optional[LigneDevis]:
        """Recherche une ligne par son ID.

        Args:
            ligne_id: L'ID de la ligne.

        Returns:
            La ligne ou None si non trouvee.
        """
        pass

    @abstractmethod
    def find_by_lot(
        self,
        lot_devis_id: int,
        limit: int = 100,
        offset: int = 0,
    ) -> List[LigneDevis]:
        """Liste les lignes d'un lot de devis.

        Args:
            lot_devis_id: L'ID du lot.
            limit: Nombre maximum de resultats.
            offset: Decalage pour pagination.

        Returns:
            Liste des lignes ordonnee par le champ ordre.
        """
        pass

    @abstractmethod
    def find_by_devis(self, devis_id: int) -> List[LigneDevis]:
        """Liste toutes les lignes d'un devis (tous lots confondus).

        Args:
            devis_id: L'ID du devis.

        Returns:
            Liste des lignes.
        """
        pass

    @abstractmethod
    def somme_by_lot(self, lot_devis_id: int) -> Decimal:
        """Calcule la somme HT des lignes d'un lot.

        Args:
            lot_devis_id: L'ID du lot.

        Returns:
            La somme HT des lignes.
        """
        pass

    @abstractmethod
    def count_by_lot(self, lot_devis_id: int) -> int:
        """Compte le nombre de lignes d'un lot.

        Args:
            lot_devis_id: L'ID du lot.

        Returns:
            Le nombre de lignes.
        """
        pass

    @abstractmethod
    def delete(self, ligne_id: int, deleted_by: Optional[int] = None) -> bool:
        """Supprime une ligne (soft delete - H10).

        Args:
            ligne_id: L'ID de la ligne a supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.

        Returns:
            True si supprimee, False si non trouvee.
        """
        pass
