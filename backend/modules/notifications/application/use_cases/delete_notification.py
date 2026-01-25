"""Use case: Supprimer des notifications."""

from dataclasses import dataclass
from typing import Optional

from ...domain.repositories import NotificationRepository


@dataclass
class DeleteNotificationUseCase:
    """
    Supprime une ou toutes les notifications d'un utilisateur.
    """

    repository: NotificationRepository

    def execute(
        self,
        user_id: int,
        notification_id: Optional[int] = None,
    ) -> int:
        """
        Execute le use case.

        Args:
            user_id: ID de l'utilisateur (pour validation).
            notification_id: ID de la notification a supprimer.
                            Si None, supprime toutes les notifications.

        Returns:
            Nombre de notifications supprimees.

        Raises:
            ValueError: Si la notification n'appartient pas a l'utilisateur.
        """
        if notification_id is None:
            # Supprimer toutes les notifications
            return self.repository.delete_all_for_user(user_id)

        # Supprimer une notification specifique
        notification = self.repository.find_by_id(notification_id)
        if not notification:
            return 0

        if notification.user_id != user_id:
            raise ValueError("Cette notification ne vous appartient pas")

        self.repository.delete(notification_id)
        return 1
