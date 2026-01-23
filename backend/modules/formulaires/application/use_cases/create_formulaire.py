"""Use Case CreateFormulaire - Creation d'un formulaire (FOR-11)."""

from typing import Optional, Callable

from ...domain.entities import FormulaireRempli
from ...domain.repositories import (
    FormulaireRempliRepository,
    TemplateFormulaireRepository,
)
from ...domain.events import FormulaireCreatedEvent
from ..dtos import CreateFormulaireDTO, FormulaireRempliDTO


class TemplateNotFoundError(Exception):
    """Erreur levee si le template n'est pas trouve."""

    pass


class TemplateInactiveError(Exception):
    """Erreur levee si le template est inactif."""

    pass


class CreateFormulaireUseCase:
    """
    Use Case pour creer un formulaire a remplir.

    Implemente FOR-11 - Lien direct "Remplir le formulaire".
    """

    def __init__(
        self,
        formulaire_repo: FormulaireRempliRepository,
        template_repo: TemplateFormulaireRepository,
        event_publisher: Optional[Callable] = None,
    ):
        """
        Initialise le use case.

        Args:
            formulaire_repo: Repository des formulaires.
            template_repo: Repository des templates.
            event_publisher: Fonction pour publier les evenements.
        """
        self._formulaire_repo = formulaire_repo
        self._template_repo = template_repo
        self._event_publisher = event_publisher

    def execute(self, dto: CreateFormulaireDTO) -> FormulaireRempliDTO:
        """
        Execute la creation d'un formulaire.

        Args:
            dto: Les donnees du formulaire a creer.

        Returns:
            Le formulaire cree.

        Raises:
            TemplateNotFoundError: Si le template n'existe pas.
            TemplateInactiveError: Si le template est inactif.
        """
        # Verifier que le template existe et est actif
        template = self._template_repo.find_by_id(dto.template_id)
        if not template:
            raise TemplateNotFoundError(
                f"Template {dto.template_id} non trouve"
            )

        if not template.is_active:
            raise TemplateInactiveError(
                f"Le template '{template.nom}' est inactif"
            )

        # Creer le formulaire
        formulaire = FormulaireRempli(
            template_id=dto.template_id,
            chantier_id=dto.chantier_id,
            user_id=dto.user_id,
        )

        # Ajouter la localisation si fournie (FOR-03)
        if dto.latitude is not None and dto.longitude is not None:
            formulaire.set_localisation(dto.latitude, dto.longitude)

        # Sauvegarder
        saved = self._formulaire_repo.save(formulaire)

        # Publier l'evenement
        if self._event_publisher:
            event = FormulaireCreatedEvent(
                formulaire_id=saved.id,
                template_id=saved.template_id,
                chantier_id=saved.chantier_id,
                user_id=saved.user_id,
            )
            self._event_publisher(event)

        return FormulaireRempliDTO.from_entity(saved)
