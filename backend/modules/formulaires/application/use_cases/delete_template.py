"""Use Case DeleteTemplate - Suppression d'un template de formulaire."""

from typing import Optional, Callable

from ...domain.repositories import TemplateFormulaireRepository
from ...domain.events import TemplateDeletedEvent


class TemplateNotFoundError(Exception):
    """Erreur levee si le template n'est pas trouve."""

    pass


class DeleteTemplateUseCase:
    """Use Case pour supprimer un template de formulaire."""

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

    def execute(self, template_id: int, deleted_by: Optional[int] = None) -> bool:
        """
        Execute la suppression d'un template.

        Args:
            template_id: ID du template a supprimer.
            deleted_by: ID de l'utilisateur qui supprime.

        Returns:
            True si le template a ete supprime.

        Raises:
            TemplateNotFoundError: Si le template n'existe pas.
        """
        # Recuperer le template pour l'evenement
        template = self._template_repo.find_by_id(template_id)
        if not template:
            raise TemplateNotFoundError(f"Template {template_id} non trouve")

        nom = template.nom

        # Supprimer
        result = self._template_repo.delete(template_id)

        # Publier l'evenement
        if result and self._event_publisher:
            event = TemplateDeletedEvent(
                template_id=template_id,
                nom=nom,
                deleted_by=deleted_by,
            )
            self._event_publisher(event)

        return result
