"""Domain Layer du module auth.

Ce module contient la logique métier pure :
- Entités (User)
- Value Objects (Email, Role, PasswordHash)
- Interfaces Repository (UserRepository)
- Domain Events (UserCreatedEvent, etc.)
- Domain Services (PasswordService interface)

RÈGLE : Aucune dépendance vers des frameworks externes.
"""

from .entities import User
from .value_objects import Email, PasswordHash, Role
from .repositories import UserRepository
from .events import (
    UserCreatedEvent,
    UserLoggedInEvent,
    UserDeactivatedEvent,
    UserRoleChangedEvent,
)
from .services import PasswordService

__all__ = [
    # Entities
    "User",
    # Value Objects
    "Email",
    "PasswordHash",
    "Role",
    # Repositories
    "UserRepository",
    # Events
    "UserCreatedEvent",
    "UserLoggedInEvent",
    "UserDeactivatedEvent",
    "UserRoleChangedEvent",
    # Services
    "PasswordService",
]
