"""Persistence du module notifications."""

from .models import NotificationModel
from .sqlalchemy_notification_repository import SQLAlchemyNotificationRepository

__all__ = ["NotificationModel", "SQLAlchemyNotificationRepository"]
