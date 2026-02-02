"""Interface du repository pour les signatures electroniques de devis.

DEV-14: Signature electronique client.
"""

from abc import ABC, abstractmethod
from typing import Optional

from ..entities.signature_devis import SignatureDevis


class SignatureDevisRepository(ABC):
    """Interface abstraite pour la persistence des signatures electroniques.

    Note:
        Le Domain ne connait pas l'implementation.
        L'infrastructure fournit l'implementation concrete (SQLAlchemy).
    """

    @abstractmethod
    def find_by_id(self, signature_id: int) -> Optional[SignatureDevis]:
        """Trouve une signature electronique par son ID.

        Args:
            signature_id: L'ID de la signature.

        Returns:
            La signature ou None si non trouvee.
        """
        pass

    @abstractmethod
    def find_by_devis_id(self, devis_id: int) -> Optional[SignatureDevis]:
        """Trouve la signature electronique associee a un devis.

        Un devis ne peut avoir qu'une seule signature active (UNIQUE sur devis_id).

        Args:
            devis_id: L'ID du devis.

        Returns:
            La signature ou None si non trouvee.
        """
        pass

    @abstractmethod
    def save(self, signature: SignatureDevis) -> SignatureDevis:
        """Persiste une signature electronique (creation ou mise a jour).

        Args:
            signature: La signature a persister.

        Returns:
            La signature avec son ID attribue.
        """
        pass

    @abstractmethod
    def delete(self, signature_id: int) -> bool:
        """Supprime une signature electronique.

        Args:
            signature_id: L'ID de la signature a supprimer.

        Returns:
            True si supprimee, False si non trouvee.
        """
        pass
