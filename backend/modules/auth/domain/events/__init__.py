"""Domain Events du module auth."""

from .user_events import (
    UserCreatedEvent,
    UserLoggedInEvent,
    UserDeactivatedEvent,
    UserRoleChangedEvent,
)

__all__ = [
    "UserCreatedEvent",
    "UserLoggedInEvent",
    "UserDeactivatedEvent",
    "UserRoleChangedEvent",
]
