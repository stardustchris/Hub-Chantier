"""Use case: Creer une notification."""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List

from ...domain.entities import Notification
from ...domain.value_objects import NotificationType
from ...domain.repositories import NotificationRepository
from ..dtos import NotificationDTO


@dataclass
class CreateNotificationUseCase:
    """
    Cree une notification pour un utilisateur.

    Utilisable par les event handlers pour creer des notifications
    suite a des evenements (commentaire, mention, document, etc.).
    """

    repository: NotificationRepository

    def execute(
        self,
        user_id: int,
        notification_type: NotificationType,
        title: str,
        message: str,
        related_post_id: Optional[int] = None,
        related_comment_id: Optional[int] = None,
        related_chantier_id: Optional[int] = None,
        related_document_id: Optional[int] = None,
        triggered_by_user_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> NotificationDTO:
        """
        Execute le use case.

        Args:
            user_id: ID de l'utilisateur destinataire.
            notification_type: Type de notification.
            title: Titre court.
            message: Message detaille.
            related_post_id: ID du post concerne.
            related_comment_id: ID du commentaire concerne.
            related_chantier_id: ID du chantier concerne.
            related_document_id: ID du document concerne.
            triggered_by_user_id: ID de l'utilisateur ayant declenche.
            metadata: Donnees supplementaires.

        Returns:
            DTO de la notification creee.
        """
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            related_post_id=related_post_id,
            related_comment_id=related_comment_id,
            related_chantier_id=related_chantier_id,
            related_document_id=related_document_id,
            triggered_by_user_id=triggered_by_user_id,
            metadata=metadata or {},
        )

        saved = self.repository.save(notification)

        return NotificationDTO(
            id=saved.id,
            user_id=saved.user_id,
            type=saved.type.value,
            title=saved.title,
            message=saved.message,
            is_read=saved.is_read,
            read_at=saved.read_at,
            related_post_id=saved.related_post_id,
            related_comment_id=saved.related_comment_id,
            related_chantier_id=saved.related_chantier_id,
            related_document_id=saved.related_document_id,
            triggered_by_user_id=saved.triggered_by_user_id,
            metadata=saved.metadata,
            created_at=saved.created_at,
        )

    def execute_batch(
        self,
        user_ids: List[int],
        notification_type: NotificationType,
        title: str,
        message: str,
        related_post_id: Optional[int] = None,
        related_comment_id: Optional[int] = None,
        related_chantier_id: Optional[int] = None,
        related_document_id: Optional[int] = None,
        triggered_by_user_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> List[NotificationDTO]:
        """
        Cree des notifications pour plusieurs utilisateurs.

        Args:
            user_ids: Liste des IDs des utilisateurs destinataires.
            ... (memes parametres que execute)

        Returns:
            Liste des DTOs des notifications creees.
        """
        notifications = [
            Notification(
                user_id=user_id,
                type=notification_type,
                title=title,
                message=message,
                related_post_id=related_post_id,
                related_comment_id=related_comment_id,
                related_chantier_id=related_chantier_id,
                related_document_id=related_document_id,
                triggered_by_user_id=triggered_by_user_id,
                metadata=metadata or {},
            )
            for user_id in user_ids
        ]

        saved_notifications = self.repository.save_many(notifications)

        return [
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
            for n in saved_notifications
        ]
