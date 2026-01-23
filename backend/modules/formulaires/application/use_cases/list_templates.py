"""Use Case ListTemplates - Liste des templates de formulaire (FOR-01)."""

from dataclasses import dataclass
from typing import Optional, List

from ...domain.repositories import TemplateFormulaireRepository
from ...domain.value_objects import CategorieFormulaire
from ..dtos import TemplateFormulaireDTO


@dataclass
class ListTemplatesResult:
    """Resultat de la liste des templates."""

    templates: List[TemplateFormulaireDTO]
    total: int
    skip: int
    limit: int


class ListTemplatesUseCase:
    """
    Use Case pour lister les templates de formulaire.

    Implemente FOR-01 - Templates personnalises.
    """

    def __init__(self, template_repo: TemplateFormulaireRepository):
        """
        Initialise le use case.

        Args:
            template_repo: Repository des templates.
        """
        self._template_repo = template_repo

    def execute(
        self,
        query: Optional[str] = None,
        categorie: Optional[str] = None,
        active_only: bool = False,
        skip: int = 0,
        limit: int = 100,
    ) -> ListTemplatesResult:
        """
        Execute la liste des templates.

        Args:
            query: Texte de recherche (optionnel).
            categorie: Filtrer par categorie (optionnel).
            active_only: Filtrer les actifs uniquement.
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum d'elements.

        Returns:
            Le resultat de la recherche.
        """
        cat = None
        if categorie:
            cat = CategorieFormulaire.from_string(categorie)

        templates, total = self._template_repo.search(
            query=query,
            categorie=cat,
            active_only=active_only,
            skip=skip,
            limit=limit,
        )

        return ListTemplatesResult(
            templates=[TemplateFormulaireDTO.from_entity(t) for t in templates],
            total=total,
            skip=skip,
            limit=limit,
        )

    def execute_by_categorie(
        self,
        categorie: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TemplateFormulaireDTO]:
        """
        Liste les templates d'une categorie.

        Args:
            categorie: La categorie.
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum d'elements.

        Returns:
            Liste des templates.
        """
        cat = CategorieFormulaire.from_string(categorie)
        templates = self._template_repo.find_by_categorie(cat, skip, limit)
        return [TemplateFormulaireDTO.from_entity(t) for t in templates]

    def execute_active(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TemplateFormulaireDTO]:
        """
        Liste les templates actifs.

        Args:
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum d'elements.

        Returns:
            Liste des templates actifs.
        """
        templates = self._template_repo.find_active(skip, limit)
        return [TemplateFormulaireDTO.from_entity(t) for t in templates]
