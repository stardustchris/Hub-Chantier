"""Dependencies pour le module notifications."""

from fastapi import Depends
from sqlalchemy.orm import Session

from shared.infrastructure import get_db
from ..persistence import SQLAlchemyNotificationRepository
from ...application.use_cases import (
    GetNotificationsUseCase,
    MarkAsReadUseCase,
    CreateNotificationUseCase,
    DeleteNotificationUseCase,
)


def get_notification_repository(
    db: Session = Depends(get_db),
) -> SQLAlchemyNotificationRepository:
    """Fournit le repository de notifications."""
    return SQLAlchemyNotificationRepository(db)


def get_notifications_use_case(
    repository: SQLAlchemyNotificationRepository = Depends(get_notification_repository),
) -> GetNotificationsUseCase:
    """Fournit le use case GetNotifications."""
    return GetNotificationsUseCase(repository=repository)


def get_mark_as_read_use_case(
    repository: SQLAlchemyNotificationRepository = Depends(get_notification_repository),
) -> MarkAsReadUseCase:
    """Fournit le use case MarkAsRead."""
    return MarkAsReadUseCase(repository=repository)


def get_create_notification_use_case(
    repository: SQLAlchemyNotificationRepository = Depends(get_notification_repository),
) -> CreateNotificationUseCase:
    """Fournit le use case CreateNotification."""
    return CreateNotificationUseCase(repository=repository)


def get_delete_notification_use_case(
    repository: SQLAlchemyNotificationRepository = Depends(get_notification_repository),
) -> DeleteNotificationUseCase:
    """Fournit le use case DeleteNotification."""
    return DeleteNotificationUseCase(repository=repository)
