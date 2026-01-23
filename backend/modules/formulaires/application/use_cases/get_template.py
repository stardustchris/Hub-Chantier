"""Use Case GetTemplate - Recuperation d'un template de formulaire."""

from typing import Optional

from ...domain.repositories import TemplateFormulaireRepository
from ..dtos import TemplateFormulaireDTO


class TemplateNotFoundError(Exception):
    """Erreur levee si le template n'est pas trouve."""

    pass


class GetTemplateUseCase:
    """Use Case pour recuperer un template de formulaire."""

    def __init__(self, template_repo: TemplateFormulaireRepository):
        """
        Initialise le use case.

        Args:
            template_repo: Repository des templates.
        """
        self._template_repo = template_repo

    def execute(self, template_id: int) -> TemplateFormulaireDTO:
        """
        Execute la recuperation d'un template.

        Args:
            template_id: ID du template a recuperer.

        Returns:
            Le template trouve.

        Raises:
            TemplateNotFoundError: Si le template n'existe pas.
        """
        template = self._template_repo.find_by_id(template_id)
        if not template:
            raise TemplateNotFoundError(f"Template {template_id} non trouve")

        return TemplateFormulaireDTO.from_entity(template)

    def execute_by_nom(self, nom: str) -> Optional[TemplateFormulaireDTO]:
        """
        Recupere un template par son nom.

        Args:
            nom: Nom du template.

        Returns:
            Le template trouve ou None.
        """
        template = self._template_repo.find_by_nom(nom)
        if not template:
            return None
        return TemplateFormulaireDTO.from_entity(template)
