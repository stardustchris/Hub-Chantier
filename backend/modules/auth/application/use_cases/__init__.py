"""Use Cases du module auth."""

from .login import LoginUseCase, InvalidCredentialsError, UserInactiveError
from .register import RegisterUseCase, EmailAlreadyExistsError, WeakPasswordError, CodeAlreadyExistsError
from .get_current_user import GetCurrentUserUseCase, InvalidTokenError, UserNotFoundError
from .update_user import UpdateUserUseCase
from .deactivate_user import DeactivateUserUseCase, ActivateUserUseCase
from .list_users import ListUsersUseCase, GetUserByIdUseCase

__all__ = [
    # Use Cases
    "LoginUseCase",
    "RegisterUseCase",
    "GetCurrentUserUseCase",
    "UpdateUserUseCase",
    "DeactivateUserUseCase",
    "ActivateUserUseCase",
    "ListUsersUseCase",
    "GetUserByIdUseCase",
    # Exceptions
    "InvalidCredentialsError",
    "UserInactiveError",
    "EmailAlreadyExistsError",
    "CodeAlreadyExistsError",
    "WeakPasswordError",
    "InvalidTokenError",
    "UserNotFoundError",
]
