"""Use Case GetFormulaire - Recuperation d'un formulaire."""

from ...domain.repositories import FormulaireRempliRepository
from ..dtos import FormulaireRempliDTO


class FormulaireNotFoundError(Exception):
    """Erreur levee si le formulaire n'est pas trouve."""

    pass


class GetFormulaireUseCase:
    """Use Case pour recuperer un formulaire."""

    def __init__(self, formulaire_repo: FormulaireRempliRepository):
        """
        Initialise le use case.

        Args:
            formulaire_repo: Repository des formulaires.
        """
        self._formulaire_repo = formulaire_repo

    def execute(self, formulaire_id: int) -> FormulaireRempliDTO:
        """
        Execute la recuperation d'un formulaire.

        Args:
            formulaire_id: ID du formulaire a recuperer.

        Returns:
            Le formulaire trouve.

        Raises:
            FormulaireNotFoundError: Si le formulaire n'existe pas.
        """
        formulaire = self._formulaire_repo.find_by_id(formulaire_id)
        if not formulaire:
            raise FormulaireNotFoundError(
                f"Formulaire {formulaire_id} non trouve"
            )

        return FormulaireRempliDTO.from_entity(formulaire)
