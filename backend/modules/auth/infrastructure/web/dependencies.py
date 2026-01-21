"""Dépendances FastAPI pour le module auth."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ...adapters.controllers import AuthController
from ...adapters.providers import BcryptPasswordService, JWTTokenService
from ...application.use_cases import (
    LoginUseCase,
    RegisterUseCase,
    GetCurrentUserUseCase,
)
from ..persistence import SQLAlchemyUserRepository
from shared.infrastructure.database import get_db
from shared.infrastructure.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_password_service() -> BcryptPasswordService:
    """Retourne le service de hash des mots de passe."""
    return BcryptPasswordService()


def get_token_service() -> JWTTokenService:
    """Retourne le service de génération de tokens."""
    return JWTTokenService(
        secret_key=settings.SECRET_KEY,
        expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )


def get_user_repository(db: Session = Depends(get_db)) -> SQLAlchemyUserRepository:
    """Retourne le repository utilisateurs."""
    return SQLAlchemyUserRepository(db)


def get_login_use_case(
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    password_service: BcryptPasswordService = Depends(get_password_service),
    token_service: JWTTokenService = Depends(get_token_service),
) -> LoginUseCase:
    """Retourne le use case de connexion."""
    return LoginUseCase(
        user_repo=user_repo,
        password_service=password_service,
        token_service=token_service,
    )


def get_register_use_case(
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    password_service: BcryptPasswordService = Depends(get_password_service),
    token_service: JWTTokenService = Depends(get_token_service),
) -> RegisterUseCase:
    """Retourne le use case d'inscription."""
    return RegisterUseCase(
        user_repo=user_repo,
        password_service=password_service,
        token_service=token_service,
    )


def get_current_user_use_case(
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
    token_service: JWTTokenService = Depends(get_token_service),
) -> GetCurrentUserUseCase:
    """Retourne le use case de récupération utilisateur."""
    return GetCurrentUserUseCase(
        user_repo=user_repo,
        token_service=token_service,
    )


def get_auth_controller(
    login_use_case: LoginUseCase = Depends(get_login_use_case),
    register_use_case: RegisterUseCase = Depends(get_register_use_case),
    get_current_user_use_case: GetCurrentUserUseCase = Depends(get_current_user_use_case),
) -> AuthController:
    """Retourne le controller d'authentification."""
    return AuthController(
        login_use_case=login_use_case,
        register_use_case=register_use_case,
        get_current_user_use_case=get_current_user_use_case,
    )


def get_current_user_id(
    token: str = Depends(oauth2_scheme),
    token_service: JWTTokenService = Depends(get_token_service),
) -> int:
    """
    Extrait l'ID utilisateur du token JWT.

    Args:
        token: Le token JWT.
        token_service: Service de validation des tokens.

    Returns:
        L'ID de l'utilisateur.

    Raises:
        HTTPException 401: Si le token est invalide.
    """
    user_id = token_service.get_user_id(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id
