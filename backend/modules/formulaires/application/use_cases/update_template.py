"""Use Case UpdateTemplate - Mise a jour d'un template de formulaire."""

from typing import Optional, Callable

from ...domain.entities import ChampTemplate
from ...domain.value_objects import CategorieFormulaire, TypeChamp
from ...domain.repositories import TemplateFormulaireRepository
from ...domain.events import TemplateUpdatedEvent
from ..dtos import UpdateTemplateDTO, TemplateFormulaireDTO


class TemplateNotFoundError(Exception):
    """Erreur levee si le template n'est pas trouve."""

    pass


class UpdateTemplateUseCase:
    """Use Case pour mettre a jour un template de formulaire."""

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

    def execute(
        self,
        template_id: int,
        dto: UpdateTemplateDTO,
        updated_by: Optional[int] = None,
    ) -> TemplateFormulaireDTO:
        """
        Execute la mise a jour d'un template.

        Args:
            template_id: ID du template a mettre a jour.
            dto: Les donnees de mise a jour.
            updated_by: ID de l'utilisateur qui met a jour.

        Returns:
            Le template mis a jour.

        Raises:
            TemplateNotFoundError: Si le template n'existe pas.
        """
        # Recuperer le template
        template = self._template_repo.find_by_id(template_id)
        if not template:
            raise TemplateNotFoundError(f"Template {template_id} non trouve")

        # Mettre a jour les champs de base
        template.update(
            nom=dto.nom,
            description=dto.description,
            categorie=(
                CategorieFormulaire.from_string(dto.categorie)
                if dto.categorie
                else None
            ),
        )

        # Mettre a jour le statut actif
        if dto.is_active is not None:
            if dto.is_active:
                template.activer()
            else:
                template.desactiver()

        # Mettre a jour les champs si fournis
        if dto.champs is not None:
            # Vider les champs existants et ajouter les nouveaux
            template.champs = []
            for champ_dto in dto.champs:
                champ = ChampTemplate(
                    id=champ_dto.id,
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

            # Incrementer la version (FOR-08)
            template.incrementer_version()

        # Sauvegarder
        saved_template = self._template_repo.save(template)

        # Publier l'evenement
        if self._event_publisher:
            event = TemplateUpdatedEvent(
                template_id=saved_template.id,
                nom=saved_template.nom,
                version=saved_template.version,
                updated_by=updated_by,
            )
            self._event_publisher(event)

        return TemplateFormulaireDTO.from_entity(saved_template)
