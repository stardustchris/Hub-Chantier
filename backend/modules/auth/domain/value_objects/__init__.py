"""Value Objects du module auth."""

from .email import Email
from .password_hash import PasswordHash
from .role import Role

__all__ = ["Email", "PasswordHash", "Role"]
