"""Infrastructure du module notifications."""

from .persistence import NotificationModel, SQLAlchemyNotificationRepository
from .web import router

__all__ = ["NotificationModel", "SQLAlchemyNotificationRepository", "router"]
