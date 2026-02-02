"""Interface du repository pour les frais de chantier.

DEV-25: Frais de chantier - Compte prorata, frais generaux, installations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.frais_chantier_devis import FraisChantierDevis


class FraisChantierRepository(ABC):
    """Interface abstraite pour la persistence des frais de chantier.

    Note:
        Le Domain ne connait pas l'implementation.
        L'infrastructure fournit l'implementation concrete (SQLAlchemy).
    """

    @abstractmethod
    def find_by_id(self, frais_id: int) -> Optional[FraisChantierDevis]:
        """Trouve un frais de chantier par son ID.

        Args:
            frais_id: L'ID du frais de chantier.

        Returns:
            Le frais de chantier ou None si non trouve.
        """
        pass

    @abstractmethod
    def find_by_devis(self, devis_id: int) -> List[FraisChantierDevis]:
        """Liste les frais de chantier d'un devis (non supprimes).

        Args:
            devis_id: L'ID du devis.

        Returns:
            Liste des frais de chantier, triee par ordre.
        """
        pass

    @abstractmethod
    def save(self, frais: FraisChantierDevis) -> FraisChantierDevis:
        """Persiste un frais de chantier (creation ou mise a jour).

        Args:
            frais: Le frais de chantier a persister.

        Returns:
            Le frais avec son ID attribue.
        """
        pass

    @abstractmethod
    def delete(self, frais_id: int, deleted_by: int) -> bool:
        """Supprime un frais de chantier (soft delete).

        Args:
            frais_id: L'ID du frais a supprimer.
            deleted_by: L'ID de l'utilisateur qui supprime.

        Returns:
            True si supprime, False si non trouve.
        """
        pass
