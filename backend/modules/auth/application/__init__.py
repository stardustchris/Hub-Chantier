"""Application Layer du module auth.

Ce module contient la logique applicative :
- Use Cases (Login, Register, GetCurrentUser)
- DTOs (UserDTO, LoginDTO, etc.)
- Ports (TokenService interface)

RÈGLE : Dépend uniquement du Domain, pas de l'Infrastructure.
"""

from .use_cases import (
    LoginUseCase,
    RegisterUseCase,
    GetCurrentUserUseCase,
    InvalidCredentialsError,
    UserInactiveError,
    EmailAlreadyExistsError,
    WeakPasswordError,
    InvalidTokenError,
    UserNotFoundError,
)
from .dtos import UserDTO, LoginDTO, RegisterDTO, TokenDTO, AuthResponseDTO
from .ports import TokenService, TokenPayload

__all__ = [
    # Use Cases
    "LoginUseCase",
    "RegisterUseCase",
    "GetCurrentUserUseCase",
    # DTOs
    "UserDTO",
    "LoginDTO",
    "RegisterDTO",
    "TokenDTO",
    "AuthResponseDTO",
    # Ports
    "TokenService",
    "TokenPayload",
    # Exceptions
    "InvalidCredentialsError",
    "UserInactiveError",
    "EmailAlreadyExistsError",
    "WeakPasswordError",
    "InvalidTokenError",
    "UserNotFoundError",
]
