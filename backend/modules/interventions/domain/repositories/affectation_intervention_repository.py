"""Interface du repository AffectationIntervention."""

from abc import ABC, abstractmethod
from typing import Optional, List

from ..entities import AffectationIntervention


class AffectationInterventionRepository(ABC):
    """Interface abstraite pour le repository des affectations d'intervention."""

    @abstractmethod
    async def save(
        self, affectation: AffectationIntervention
    ) -> AffectationIntervention:
        """Sauvegarde une affectation.

        Args:
            affectation: L'affectation a sauvegarder.

        Returns:
            L'affectation avec son ID assigne.
        """
        pass

    @abstractmethod
    async def get_by_id(
        self, affectation_id: int
    ) -> Optional[AffectationIntervention]:
        """Recupere une affectation par son ID.

        Args:
            affectation_id: L'identifiant de l'affectation.

        Returns:
            L'affectation ou None si non trouvee.
        """
        pass

    @abstractmethod
    async def list_by_intervention(
        self,
        intervention_id: int,
        include_deleted: bool = False,
    ) -> List[AffectationIntervention]:
        """Liste les affectations d'une intervention.

        INT-10: Affectation technicien

        Args:
            intervention_id: ID de l'intervention.
            include_deleted: Inclure les affectations supprimees.

        Returns:
            Liste des affectations.
        """
        pass

    @abstractmethod
    async def list_by_utilisateur(
        self,
        utilisateur_id: int,
        include_deleted: bool = False,
    ) -> List[AffectationIntervention]:
        """Liste les affectations d'un utilisateur.

        Args:
            utilisateur_id: ID de l'utilisateur.
            include_deleted: Inclure les affectations supprimees.

        Returns:
            Liste des affectations.
        """
        pass

    @abstractmethod
    async def get_principal(
        self, intervention_id: int
    ) -> Optional[AffectationIntervention]:
        """Recupere le technicien principal d'une intervention.

        Args:
            intervention_id: ID de l'intervention.

        Returns:
            L'affectation du technicien principal ou None.
        """
        pass

    @abstractmethod
    async def exists(
        self,
        intervention_id: int,
        utilisateur_id: int,
    ) -> bool:
        """Verifie si une affectation existe.

        Args:
            intervention_id: ID de l'intervention.
            utilisateur_id: ID de l'utilisateur.

        Returns:
            True si l'affectation existe.
        """
        pass

    @abstractmethod
    async def delete(
        self, affectation_id: int, deleted_by: int
    ) -> bool:
        """Supprime une affectation (soft delete).

        Args:
            affectation_id: ID de l'affectation.
            deleted_by: ID de l'utilisateur qui supprime.

        Returns:
            True si supprimee.
        """
        pass

    @abstractmethod
    async def delete_by_intervention(
        self, intervention_id: int, deleted_by: int
    ) -> int:
        """Supprime toutes les affectations d'une intervention.

        Args:
            intervention_id: ID de l'intervention.
            deleted_by: ID de l'utilisateur qui supprime.

        Returns:
            Nombre d'affectations supprimees.
        """
        pass
