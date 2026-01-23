"""Use Case CreateTemplate - Creation d'un template de formulaire (FOR-01)."""

from typing import Optional, Callable

from ...domain.entities import TemplateFormulaire, ChampTemplate
from ...domain.value_objects import CategorieFormulaire, TypeChamp
from ...domain.repositories import TemplateFormulaireRepository
from ...domain.events import TemplateCreatedEvent
from ..dtos import CreateTemplateDTO, TemplateFormulaireDTO


class TemplateAlreadyExistsError(Exception):
    """Erreur levee si un template avec ce nom existe deja."""

    pass


class CreateTemplateUseCase:
    """
    Use Case pour creer un template de formulaire.

    Implemente FOR-01 - Templates personnalises.
    """

    def __init__(
        self,
        template_repo: TemplateFormulaireRepository,
        event_publisher: Optional[Callable] = None,
    ):
        """
        Initialise le use case.

        Args:
            template_repo: Repository des templates.
            event_publisher: Fonction pour publier les evenements.
        """
        self._template_repo = template_repo
        self._event_publisher = event_publisher

    def execute(self, dto: CreateTemplateDTO) -> TemplateFormulaireDTO:
        """
        Execute la creation d'un template.

        Args:
            dto: Les donnees du template a creer.

        Returns:
            Le template cree.

        Raises:
            TemplateAlreadyExistsError: Si un template avec ce nom existe deja.
        """
        # Verifier unicite du nom
        if self._template_repo.exists_by_nom(dto.nom):
            raise TemplateAlreadyExistsError(
                f"Un template avec le nom '{dto.nom}' existe deja"
            )

        # Creer l'entite
        template = TemplateFormulaire(
            nom=dto.nom,
            categorie=CategorieFormulaire.from_string(dto.categorie),
            description=dto.description,
            created_by=dto.created_by,
        )

        # Ajouter les champs
        for champ_dto in dto.champs:
            champ = ChampTemplate(
                nom=champ_dto.nom,
                label=champ_dto.label,
                type_champ=TypeChamp.from_string(champ_dto.type_champ),
                obligatoire=champ_dto.obligatoire,
                ordre=champ_dto.ordre,
                placeholder=champ_dto.placeholder,
                options=champ_dto.options,
                valeur_defaut=champ_dto.valeur_defaut,
                validation_regex=champ_dto.validation_regex,
                min_value=champ_dto.min_value,
                max_value=champ_dto.max_value,
            )
            template.ajouter_champ(champ)

        # Sauvegarder
        saved_template = self._template_repo.save(template)

        # Publier l'evenement
        if self._event_publisher:
            event = TemplateCreatedEvent(
                template_id=saved_template.id,
                nom=saved_template.nom,
                categorie=saved_template.categorie.value,
                created_by=saved_template.created_by,
            )
            self._event_publisher(event)

        return TemplateFormulaireDTO.from_entity(saved_template)
