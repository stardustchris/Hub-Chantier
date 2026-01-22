"""Use Case GetAffectation - Récupération d'une affectation."""

from typing import Optional

from ...domain.repositories import AffectationRepository
from ..dtos import AffectationDTO


class AffectationNotFoundError(Exception):
    """Exception levée quand l'affectation n'existe pas."""

    def __init__(self, affectation_id: int):
        self.affectation_id = affectation_id
        self.message = f"Affectation {affectation_id} non trouvée"
        super().__init__(self.message)


class GetAffectationUseCase:
    """
    Cas d'utilisation : Récupération d'une affectation par son ID.

    Attributes:
        affectation_repo: Repository pour accéder aux affectations.
    """

    def __init__(self, affectation_repo: AffectationRepository):
        """
        Initialise le use case.

        Args:
            affectation_repo: Repository affectations (interface).
        """
        self.affectation_repo = affectation_repo

    def execute(self, affectation_id: int) -> AffectationDTO:
        """
        Récupère une affectation par son ID.

        Args:
            affectation_id: ID de l'affectation à récupérer.

        Returns:
            AffectationDTO contenant l'affectation.

        Raises:
            AffectationNotFoundError: Si l'affectation n'existe pas.
        """
        affectation = self.affectation_repo.find_by_id(affectation_id)

        if not affectation:
            raise AffectationNotFoundError(affectation_id)

        return AffectationDTO.from_entity(affectation)
