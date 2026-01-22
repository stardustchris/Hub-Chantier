"""Use Case ListTemplates - Liste des modeles de taches (TAC-04)."""

from typing import Optional

from ...domain.repositories import TemplateModeleRepository
from ..dtos import TemplateModeleDTO, TemplateModeleListDTO


class ListTemplatesUseCase:
    """
    Cas d'utilisation : Liste des modeles de taches.

    Selon CDC Section 13 - TAC-04: Bibliotheque de modeles.

    Attributes:
        template_repo: Repository pour acceder aux templates.
    """

    def __init__(self, template_repo: TemplateModeleRepository):
        """
        Initialise le use case.

        Args:
            template_repo: Repository templates (interface).
        """
        self.template_repo = template_repo

    def execute(
        self,
        query: Optional[str] = None,
        categorie: Optional[str] = None,
        active_only: bool = True,
        page: int = 1,
        size: int = 50,
    ) -> TemplateModeleListDTO:
        """
        Execute la liste des templates.

        Args:
            query: Recherche textuelle.
            categorie: Filtrer par categorie.
            active_only: Filtrer les actifs uniquement.
            page: Numero de page.
            size: Nombre d'elements par page.

        Returns:
            TemplateModeleListDTO avec la liste paginee.
        """
        skip = (page - 1) * size

        # Rechercher avec filtres
        templates, total = self.template_repo.search(
            query=query,
            categorie=categorie,
            active_only=active_only,
            skip=skip,
            limit=size,
        )

        # Recuperer les categories disponibles
        categories = self.template_repo.get_categories()

        # Convertir en DTOs
        items = [TemplateModeleDTO.from_entity(t) for t in templates]

        # Calculer le nombre de pages
        pages = (total + size - 1) // size if size > 0 else 0

        return TemplateModeleListDTO(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages,
            categories=categories,
        )
