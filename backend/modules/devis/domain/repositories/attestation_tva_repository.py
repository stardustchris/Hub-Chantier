"""Interface du repository pour les attestations TVA.

DEV-23: Generation attestation TVA reglementaire.
"""

from abc import ABC, abstractmethod
from typing import Optional

from ..entities.attestation_tva import AttestationTVA


class AttestationTVARepository(ABC):
    """Interface abstraite pour la persistence des attestations TVA.

    Note:
        Le Domain ne connait pas l'implementation.
        L'infrastructure fournit l'implementation concrete (SQLAlchemy).
    """

    @abstractmethod
    def find_by_id(self, attestation_id: int) -> Optional[AttestationTVA]:
        """Trouve une attestation TVA par son ID.

        Args:
            attestation_id: L'ID de l'attestation.

        Returns:
            L'attestation TVA ou None si non trouvee.
        """
        pass

    @abstractmethod
    def find_by_devis_id(self, devis_id: int) -> Optional[AttestationTVA]:
        """Trouve l'attestation TVA associee a un devis.

        Un devis ne peut avoir qu'une seule attestation TVA.

        Args:
            devis_id: L'ID du devis.

        Returns:
            L'attestation TVA ou None si non trouvee.
        """
        pass

    @abstractmethod
    def save(self, attestation: AttestationTVA) -> AttestationTVA:
        """Persiste une attestation TVA (creation ou mise a jour).

        Args:
            attestation: L'attestation TVA a persister.

        Returns:
            L'attestation avec son ID attribue.
        """
        pass

    @abstractmethod
    def delete(self, attestation_id: int) -> bool:
        """Supprime une attestation TVA.

        Args:
            attestation_id: L'ID de l'attestation a supprimer.

        Returns:
            True si supprimee, False si non trouvee.
        """
        pass
