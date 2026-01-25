"""Notifications infrastructure - Firebase Cloud Messaging."""

from .notification_service import (
    NotificationService,
    get_notification_service,
    NotificationPayload,
)
from .handlers import ReservationNotificationHandler

__all__ = [
    "NotificationService",
    "get_notification_service",
    "NotificationPayload",
    "ReservationNotificationHandler",
]
