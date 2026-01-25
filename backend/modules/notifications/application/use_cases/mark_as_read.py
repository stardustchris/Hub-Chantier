"""Use case: Marquer des notifications comme lues."""

from dataclasses import dataclass
from typing import Optional, List

from ...domain.repositories import NotificationRepository


@dataclass
class MarkAsReadUseCase:
    """
    Marque des notifications comme lues.

    Peut marquer une notification specifique, plusieurs, ou toutes.
    """

    repository: NotificationRepository

    def execute(
        self,
        user_id: int,
        notification_ids: Optional[List[int]] = None,
    ) -> int:
        """
        Execute le use case.

        Args:
            user_id: ID de l'utilisateur (pour validation).
            notification_ids: IDs des notifications a marquer.
                             Si None, marque toutes les notifications.

        Returns:
            Nombre de notifications marquees comme lues.
        """
        if notification_ids is None:
            # Marquer toutes les notifications comme lues
            return self.repository.mark_all_as_read(user_id)

        # Marquer les notifications specifiques
        count = 0
        for notification_id in notification_ids:
            notification = self.repository.find_by_id(notification_id)
            if notification and notification.user_id == user_id:
                if not notification.is_read:
                    notification.mark_as_read()
                    self.repository.save(notification)
                    count += 1

        return count
