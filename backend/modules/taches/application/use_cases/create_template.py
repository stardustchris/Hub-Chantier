"""Use Case CreateTemplate - Creation d'un modele de taches (TAC-04)."""

from typing import Optional, Callable

from ...domain.entities import TemplateModele, SousTacheModele
from ...domain.repositories import TemplateModeleRepository
from ...domain.value_objects import UniteMesure
from ..dtos import CreateTemplateModeleDTO, TemplateModeleDTO


class TemplateAlreadyExistsError(Exception):
    """Exception levee si un template avec ce nom existe deja."""

    def __init__(self, nom: str):
        self.nom = nom
        self.message = f"Un template avec le nom '{nom}' existe deja"
        super().__init__(self.message)


class CreateTemplateUseCase:
    """
    Cas d'utilisation : Creation d'un modele de taches.

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

    def execute(self, dto: CreateTemplateModeleDTO) -> TemplateModeleDTO:
        """
        Execute la creation d'un template.

        Args:
            dto: Les donnees de creation.

        Returns:
            TemplateModeleDTO du template cree.

        Raises:
            TemplateAlreadyExistsError: Si un template avec ce nom existe.
            ValueError: Si les donnees sont invalides.
        """
        # Verifier que le nom n'existe pas
        if self.template_repo.exists_by_nom(dto.nom):
            raise TemplateAlreadyExistsError(dto.nom)

        # Valider l'unite de mesure si fournie
        unite_mesure = None
        if dto.unite_mesure:
            unite_mesure = UniteMesure.from_string(dto.unite_mesure)

        # Creer l'entite TemplateModele
        template = TemplateModele(
            nom=dto.nom,
            description=dto.description,
            categorie=dto.categorie,
            unite_mesure=unite_mesure,
            heures_estimees_defaut=dto.heures_estimees_defaut,
        )

        # Ajouter les sous-taches
        for i, st_dto in enumerate(dto.sous_taches):
            st_unite = None
            if st_dto.unite_mesure:
                st_unite = UniteMesure.from_string(st_dto.unite_mesure)

            template.ajouter_sous_tache(
                titre=st_dto.titre,
                description=st_dto.description,
                ordre=st_dto.ordre if st_dto.ordre else i,
                unite_mesure=st_unite,
                heures_estimees=st_dto.heures_estimees_defaut,
            )

        # Sauvegarder
        template = self.template_repo.save(template)

        return TemplateModeleDTO.from_entity(template)
