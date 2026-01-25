"""Dépendances FastAPI partagées entre modules.

Ce module fournit des dépendances communes pour l'authentification
et l'autorisation, évitant les imports directs entre modules.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from shared.infrastructure.database import get_db
from shared.infrastructure.config import settings

# Cookie name for JWT token
AUTH_COOKIE_NAME = "access_token"

# OAuth2 scheme for backward compatibility with Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_token_service():
    """
    Retourne le service de tokens JWT.

    Note: Import différé pour éviter les dépendances circulaires.
    """
    from modules.auth.adapters.providers import JWTTokenService
    return JWTTokenService(
        secret_key=settings.SECRET_KEY,
        expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )


def get_user_repository(db: Session = Depends(get_db)):
    """
    Retourne le repository utilisateurs.

    Note: Import différé pour éviter les dépendances circulaires.
    """
    from modules.auth.infrastructure.persistence import SQLAlchemyUserRepository
    return SQLAlchemyUserRepository(db)


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
) -> int:
    """
    Extrait l'ID utilisateur du token JWT.

    Le token peut provenir d'un cookie HttpOnly (préféré) ou de l'en-tête Authorization.

    Args:
        token: Le token JWT (depuis cookie ou header).

    Returns:
        L'ID de l'utilisateur.

    Raises:
        HTTPException 401: Si le token est invalide.
    """
    token_service = get_token_service()
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
    db: Session = Depends(get_db),
) -> str:
    """
    Récupère le rôle de l'utilisateur connecté.

    Args:
        current_user_id: ID de l'utilisateur connecté.
        db: Session de base de données.

    Returns:
        Le rôle de l'utilisateur (admin, conducteur, chef_chantier, compagnon).

    Raises:
        HTTPException 401: Si l'utilisateur n'existe pas.
    """
    user_repo = get_user_repository(db)
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


# =============================================================================
# RBAC Guards pour contrôle d'accès
# =============================================================================


def require_admin(
    current_user_role: str = Depends(get_current_user_role),
) -> str:
    """
    Guard RBAC: Requiert le rôle admin.

    Args:
        current_user_role: Rôle de l'utilisateur connecté.

    Returns:
        Le rôle si autorisé.

    Raises:
        HTTPException 403: Si l'utilisateur n'est pas admin.
    """
    if current_user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs",
        )
    return current_user_role


def require_conducteur_or_admin(
    current_user_role: str = Depends(get_current_user_role),
) -> str:
    """
    Guard RBAC: Requiert le rôle conducteur ou admin.

    Utilisé pour les actions de modification sur les chantiers.

    Args:
        current_user_role: Rôle de l'utilisateur connecté.

    Returns:
        Le rôle si autorisé.

    Raises:
        HTTPException 403: Si l'utilisateur n'est pas conducteur ou admin.
    """
    if current_user_role not in {"admin", "conducteur"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux conducteurs et administrateurs",
        )
    return current_user_role


def require_chef_or_above(
    current_user_role: str = Depends(get_current_user_role),
) -> str:
    """
    Guard RBAC: Requiert le rôle chef_chantier, conducteur ou admin.

    Utilisé pour certaines actions de lecture/modification limitées.

    Args:
        current_user_role: Rôle de l'utilisateur connecté.

    Returns:
        Le rôle si autorisé.

    Raises:
        HTTPException 403: Si l'utilisateur n'a pas les droits.
    """
    allowed_roles = {"admin", "conducteur", "chef_chantier"}
    if current_user_role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux chefs de chantier et supérieurs",
        )
    return current_user_role


# =============================================================================
# Dépendances spécifiques au filtrage par chantier
# =============================================================================


def get_current_user_chantier_ids(
    current_user_id: int = Depends(get_current_user_id),
    current_user_role: str = Depends(get_current_user_role),
    db: Session = Depends(get_db),
) -> list[int] | None:
    """
    Récupère les IDs des chantiers auxquels l'utilisateur est affecté.

    Pour les admins et conducteurs, retourne None (accès à tous les chantiers).
    Pour les chefs de chantier et compagnons, retourne la liste des chantiers
    où ils ont des affectations actives.

    Args:
        current_user_id: ID de l'utilisateur connecté.
        current_user_role: Rôle de l'utilisateur connecté.
        db: Session de base de données.

    Returns:
        Liste des IDs de chantiers, ou None pour accès global.
    """
    # Admins et conducteurs voient tous les posts
    if current_user_role in {"admin", "conducteur"}:
        return None

    # Import différé pour éviter les dépendances circulaires
    from modules.planning.infrastructure.persistence import AffectationModel
    from sqlalchemy import distinct
    from datetime import date, timedelta

    # Récupérer les chantiers avec affectations récentes (30 derniers jours)
    # pour éviter de charger tout l'historique
    date_limite = date.today() - timedelta(days=30)

    chantier_ids = (
        db.query(distinct(AffectationModel.chantier_id))
        .filter(
            AffectationModel.utilisateur_id == current_user_id,
            AffectationModel.date >= date_limite,
        )
        .all()
    )

    return [row[0] for row in chantier_ids] if chantier_ids else []
