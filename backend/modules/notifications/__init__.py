"""Module Notifications - Gestion des alertes utilisateurs."""

from .domain import Notification, NotificationType, NotificationRepository
from .application import (
    GetNotificationsUseCase,
    MarkAsReadUseCase,
    CreateNotificationUseCase,
    DeleteNotificationUseCase,
    NotificationDTO,
    NotificationListDTO,
)
from .infrastructure import router, NotificationModel

__all__ = [
    # Domain
    "Notification",
    "NotificationType",
    "NotificationRepository",
    # Application
    "GetNotificationsUseCase",
    "MarkAsReadUseCase",
    "CreateNotificationUseCase",
    "DeleteNotificationUseCase",
    "NotificationDTO",
    "NotificationListDTO",
    # Infrastructure
    "router",
    "NotificationModel",
]
