"""Use Cases pour les messages d'intervention."""

from typing import List

from ...domain.entities import InterventionMessage, TypeMessage
from ...domain.repositories import InterventionMessageRepository
from ..dtos import CreateMessageDTO


class AddMessageUseCase:
    """Use case pour ajouter un message.

    INT-11: Fil d'actualite
    INT-12: Chat intervention
    """

    def __init__(self, repository: InterventionMessageRepository):
        self._repository = repository

    def execute(
        self,
        intervention_id: int,
        dto: CreateMessageDTO,
        auteur_id: int,
    ) -> InterventionMessage:
        """Ajoute un message a l'intervention."""
        type_message = TypeMessage(dto.type_message)

        if type_message == TypeMessage.PHOTO:
            message = InterventionMessage.creer_photo(
                intervention_id=intervention_id,
                auteur_id=auteur_id,
                description=dto.contenu,
                photos_urls=dto.photos_urls,
            )
        elif type_message == TypeMessage.ACTION:
            message = InterventionMessage.creer_action(
                intervention_id=intervention_id,
                auteur_id=auteur_id,
                action=dto.contenu,
            )
        else:
            message = InterventionMessage.creer_commentaire(
                intervention_id=intervention_id,
                auteur_id=auteur_id,
                contenu=dto.contenu,
            )

        return self._repository.save(message)


class ListMessagesUseCase:
    """Use case pour lister les messages."""

    def __init__(self, repository: InterventionMessageRepository):
        self._repository = repository

    def execute(
        self,
        intervention_id: int,
        type_message: str = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[List[InterventionMessage], int]:
        """Liste les messages d'une intervention."""
        type_filter = TypeMessage(type_message) if type_message else None

        messages = self._repository.list_by_intervention(
            intervention_id=intervention_id,
            type_message=type_filter,
            limit=limit,
            offset=offset,
        )

        count = self._repository.count_by_intervention(intervention_id)

        return messages, count


class ToggleRapportInclusionUseCase:
    """Use case pour inclure/exclure un message du rapport.

    INT-15: Selection posts pour rapport
    """

    def __init__(self, repository: InterventionMessageRepository):
        self._repository = repository

    def execute(self, message_id: int, inclure: bool) -> bool:
        """Active/desactive l'inclusion dans le rapport."""
        return self._repository.toggle_inclure_rapport(message_id, inclure)
