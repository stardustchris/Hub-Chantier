"""Interface repository pour les pieces jointes de devis.

DEV-07: Insertion multimedia.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.piece_jointe_devis import PieceJointeDevis


class PieceJointeDevisRepository(ABC):
    """Interface abstraite pour la persistence des pieces jointes de devis.

    Note:
        Le Domain ne connait pas l implementation.
        L infrastructure fournit l implementation concrete (SQLAlchemy).
    """

    @abstractmethod
    def find_by_devis_id(self, devis_id: int) -> List[PieceJointeDevis]:
        """Liste toutes les pieces jointes d un devis.

        Args:
            devis_id: L ID du devis.

        Returns:
            Liste des pieces jointes, triee par ordre.
        """
        ...

    @abstractmethod
    def find_by_id(self, piece_id: int) -> Optional[PieceJointeDevis]:
        """Trouve une piece jointe par son ID.

        Args:
            piece_id: L ID de la piece jointe.

        Returns:
            La piece jointe ou None si non trouvee.
        """
        ...

    @abstractmethod
    def create(self, piece: PieceJointeDevis) -> PieceJointeDevis:
        """Cree une nouvelle piece jointe.

        Args:
            piece: La piece jointe a creer.

        Returns:
            La piece jointe avec son ID attribue.
        """
        ...

    @abstractmethod
    def update(self, piece: PieceJointeDevis) -> PieceJointeDevis:
        """Met a jour une piece jointe.

        Args:
            piece: La piece jointe avec les champs mis a jour.

        Returns:
            La piece jointe mise a jour.
        """
        ...

    @abstractmethod
    def delete(self, piece_id: int) -> bool:
        """Supprime une piece jointe (ne supprime PAS le document GED).

        Args:
            piece_id: L ID de la piece jointe a supprimer.

        Returns:
            True si supprimee, False si non trouvee.
        """
        ...
