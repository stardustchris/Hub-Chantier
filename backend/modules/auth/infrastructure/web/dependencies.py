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
    UpdateUserUseCase,
    DeactivateUserUseCase,
    ActivateUserUseCase,
    ListUsersUseCase,
    GetUserByIdUseCase,
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
