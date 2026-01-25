"""Use case: Recuperer les notifications d'un utilisateur."""

from dataclasses import dataclass
from typing import Optional

from ...domain.repositories import NotificationRepository
from ..dtos import NotificationDTO, NotificationListDTO


@dataclass
class GetNotificationsUseCase:
    """
    Recupere les notifications d'un utilisateur.

    Retourne les notifications pagnees avec le compteur de non lues.
    """

    repository: NotificationRepository

    def execute(
        self,
        user_id: int,
        unread_only: bool = False,
        skip: int = 0,
        limit: int = 50,
    ) -> NotificationListDTO:
        """
        Execute le use case.

        Args:
            user_id: ID de l'utilisateur.
            unread_only: Si True, retourne uniquement les non lues.
            skip: Nombre d'elements a sauter.
            limit: Nombre maximum a retourner.

        Returns:
            Liste des notifications avec compteurs.
        """
        notifications = self.repository.find_by_user(
            user_id=user_id,
            unread_only=unread_only,
            skip=skip,
            limit=limit,
        )

        unread_count = self.repository.count_unread(user_id)

        notification_dtos = [
            NotificationDTO(
                id=n.id,
                user_id=n.user_id,
                type=n.type.value,
                title=n.title,
                message=n.message,
                is_read=n.is_read,
                read_at=n.read_at,
                related_post_id=n.related_post_id,
                related_comment_id=n.related_comment_id,
                related_chantier_id=n.related_chantier_id,
                related_document_id=n.related_document_id,
                triggered_by_user_id=n.triggered_by_user_id,
                metadata=n.metadata,
                created_at=n.created_at,
            )
            for n in notifications
        ]

        return NotificationListDTO(
            notifications=notification_dtos,
            unread_count=unread_count,
            total=len(notification_dtos),
        )
