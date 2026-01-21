"""Use Cases du module auth."""

from .login import LoginUseCase, InvalidCredentialsError, UserInactiveError
from .register import RegisterUseCase, EmailAlreadyExistsError, WeakPasswordError
from .get_current_user import GetCurrentUserUseCase, InvalidTokenError, UserNotFoundError

__all__ = [
    # Use Cases
    "LoginUseCase",
    "RegisterUseCase",
    "GetCurrentUserUseCase",
    # Exceptions
    "InvalidCredentialsError",
    "UserInactiveError",
    "EmailAlreadyExistsError",
    "WeakPasswordError",
    "InvalidTokenError",
    "UserNotFoundError",
]
