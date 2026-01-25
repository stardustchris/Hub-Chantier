"""Interface du repository SignatureIntervention."""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities import SignatureIntervention, TypeSignataire


class SignatureInterventionRepository(ABC):
    """Interface abstraite pour le repository des signatures d'intervention."""

    @abstractmethod
    async def save(self, signature: SignatureIntervention) -> SignatureIntervention:
        """Sauvegarde une signature.

        Args:
            signature: La signature a sauvegarder.

        Returns:
            La signature avec son ID assigne.
        """
        pass

    @abstractmethod
    async def get_by_id(self, signature_id: int) -> Optional[SignatureIntervention]:
        """Recupere une signature par son ID.

        Args:
            signature_id: L'identifiant de la signature.

        Returns:
            La signature ou None si non trouvee.
        """
        pass

    @abstractmethod
    async def list_by_intervention(
        self,
        intervention_id: int,
        include_deleted: bool = False,
    ) -> List[SignatureIntervention]:
        """Liste les signatures d'une intervention.

        INT-13: Signature client
        INT-14: Signatures dans rapport PDF

        Args:
            intervention_id: ID de l'intervention.
            include_deleted: Inclure les signatures supprimees.

        Returns:
            Liste des signatures.
        """
        pass

    @abstractmethod
    async def get_signature_client(
        self, intervention_id: int
    ) -> Optional[SignatureIntervention]:
        """Recupere la signature client d'une intervention.

        Args:
            intervention_id: ID de l'intervention.

        Returns:
            La signature client ou None.
        """
        pass

    @abstractmethod
    async def get_signature_technicien(
        self, intervention_id: int, utilisateur_id: int
    ) -> Optional[SignatureIntervention]:
        """Recupere la signature d'un technicien.

        Args:
            intervention_id: ID de l'intervention.
            utilisateur_id: ID du technicien.

        Returns:
            La signature technicien ou None.
        """
        pass

    @abstractmethod
    async def has_signature_client(self, intervention_id: int) -> bool:
        """Verifie si l'intervention a une signature client.

        Args:
            intervention_id: ID de l'intervention.

        Returns:
            True si une signature client existe.
        """
        pass

    @abstractmethod
    async def has_all_signatures_techniciens(
        self, intervention_id: int
    ) -> bool:
        """Verifie si tous les techniciens ont signe.

        Args:
            intervention_id: ID de l'intervention.

        Returns:
            True si tous les techniciens affectes ont signe.
        """
        pass

    @abstractmethod
    async def delete(self, signature_id: int, deleted_by: int) -> bool:
        """Supprime une signature (soft delete).

        Args:
            signature_id: ID de la signature.
            deleted_by: ID de l'utilisateur qui supprime.

        Returns:
            True si supprimee.
        """
        pass
