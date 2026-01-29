"""Dépendances FastAPI pour le module auth."""

from typing import Optional
from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ...adapters.controllers import AuthController
from ...adapters.providers import BcryptPasswordService, JWTTokenService
from ...application.use_cases import (
    LoginUseCase,
    RegisterUseCase,
    GetCurrentUserUseCase,
    UpdateUserUseCase,
    DeactivateUserUseCase,
    ActivateUserUseCase,
    ListUsersUseCase,
    GetUserByIdUseCase,
)
from ..persistence import SQLAlchemyUserRepository
from shared.infrastructure.database import get_db
from shared.infrastructure.config import settings

# Cookie name for JWT token (must match auth_routes.py)
AUTH_COOKIE_NAME = "access_token"

# OAuth2 scheme for backward compatibility with Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


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


def get_update_user_use_case(
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
) -> UpdateUserUseCase:
    """Retourne le use case de mise à jour utilisateur."""
    return UpdateUserUseCase(user_repo=user_repo)


def get_deactivate_user_use_case(
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
) -> DeactivateUserUseCase:
    """Retourne le use case de désactivation utilisateur."""
    return DeactivateUserUseCase(user_repo=user_repo)


def get_activate_user_use_case(
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
) -> ActivateUserUseCase:
    """Retourne le use case d'activation utilisateur."""
    return ActivateUserUseCase(user_repo=user_repo)


def get_list_users_use_case(
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
) -> ListUsersUseCase:
    """Retourne le use case de liste des utilisateurs."""
    return ListUsersUseCase(user_repo=user_repo)


def get_user_by_id_use_case(
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
) -> GetUserByIdUseCase:
    """Retourne le use case de récupération par ID."""
    return GetUserByIdUseCase(user_repo=user_repo)


def get_auth_controller(
    login_use_case: LoginUseCase = Depends(get_login_use_case),
    register_use_case: RegisterUseCase = Depends(get_register_use_case),
    get_current_user_use_case: GetCurrentUserUseCase = Depends(get_current_user_use_case),
    update_user_use_case: UpdateUserUseCase = Depends(get_update_user_use_case),
    deactivate_user_use_case: DeactivateUserUseCase = Depends(get_deactivate_user_use_case),
    activate_user_use_case: ActivateUserUseCase = Depends(get_activate_user_use_case),
    list_users_use_case: ListUsersUseCase = Depends(get_list_users_use_case),
    get_user_by_id_use_case: GetUserByIdUseCase = Depends(get_user_by_id_use_case),
) -> AuthController:
    """Retourne le controller d'authentification et gestion utilisateurs."""
    return AuthController(
        login_use_case=login_use_case,
        register_use_case=register_use_case,
        get_current_user_use_case=get_current_user_use_case,
        update_user_use_case=update_user_use_case,
        deactivate_user_use_case=deactivate_user_use_case,
        activate_user_use_case=activate_user_use_case,
        list_users_use_case=list_users_use_case,
        get_user_by_id_use_case=get_user_by_id_use_case,
    )


def get_token_from_cookie_or_header(
    request: Request,
    authorization_token: Optional[str] = Depends(oauth2_scheme),
) -> str:
    """
    Extrait le token JWT depuis le cookie HttpOnly ou l'en-tête Authorization.

    Priorité: Cookie > Authorization header
    Le cookie HttpOnly est plus sécurisé car non accessible via JavaScript.

    Args:
        request: Requête HTTP pour accéder aux cookies.
        authorization_token: Token depuis Authorization header (fallback).

    Returns:
        Le token JWT.

    Raises:
        HTTPException 401: Si aucun token n'est trouvé.
    """
    # Try cookie first (more secure - HttpOnly)
    cookie_token = request.cookies.get(AUTH_COOKIE_NAME)
    if cookie_token:
        return cookie_token

    # Fallback to Authorization header for backward compatibility
    if authorization_token:
        return authorization_token

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Non authentifié",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user_id(
    token: str = Depends(get_token_from_cookie_or_header),
    token_service: JWTTokenService = Depends(get_token_service),
) -> int:
    """
    Extrait l'ID utilisateur du token JWT.

    Le token peut provenir d'un cookie HttpOnly (préféré) ou de l'en-tête Authorization.

    Args:
        token: Le token JWT (depuis cookie ou header).
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


def get_current_user_role(
    current_user_id: int = Depends(get_current_user_id),
    user_repo: SQLAlchemyUserRepository = Depends(get_user_repository),
) -> str:
    """
    Récupère le rôle de l'utilisateur connecté.

    Args:
        current_user_id: ID de l'utilisateur connecté.
        user_repo: Repository utilisateurs.

    Returns:
        Le rôle de l'utilisateur (admin, conducteur, chef_chantier, compagnon).

    Raises:
        HTTPException 401: Si l'utilisateur n'existe pas.
    """
    user = user_repo.find_by_id(current_user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user.role.value


def get_is_moderator(
    current_user_role: str = Depends(get_current_user_role),
) -> bool:
    """
    Vérifie si l'utilisateur connecté est modérateur.

    Les modérateurs sont les utilisateurs avec les rôles:
    - admin
    - conducteur

    Args:
        current_user_role: Rôle de l'utilisateur connecté.

    Returns:
        True si l'utilisateur est modérateur.
    """
    moderator_roles = {"admin", "conducteur"}
    return current_user_role in moderator_roles


def require_admin_or_conducteur(
    current_user_role: str = Depends(get_current_user_role),
) -> str:
    """
    Vérifie que l'utilisateur connecté est admin ou conducteur.

    Raises:
        HTTPException 403: Si l'utilisateur n'a pas les droits suffisants.
    """
    admin_roles = {"admin", "conducteur"}
    if current_user_role not in admin_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Droits insuffisants. Rôle admin ou conducteur requis.",
        )
    return current_user_role


def get_current_user(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    """
    Récupère l'utilisateur connecté (UserModel complet).

    Args:
        current_user_id: ID de l'utilisateur connecté.
        db: Session database.

    Returns:
        Le UserModel de l'utilisateur connecté.

    Raises:
        HTTPException 401: Si l'utilisateur n'existe pas.
    """
    from ..persistence.user_model import UserModel

    user = db.query(UserModel).filter(UserModel.id == current_user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
