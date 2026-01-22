"""Routes FastAPI pour l'authentification et gestion des utilisateurs."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

from ...adapters.controllers import AuthController
from ...application.use_cases import (
    InvalidCredentialsError,
    UserInactiveError,
    EmailAlreadyExistsError,
    CodeAlreadyExistsError,
    WeakPasswordError,
    InvalidTokenError,
    UserNotFoundError,
)
from .dependencies import get_auth_controller, get_current_user_id

router = APIRouter(prefix="/auth", tags=["auth"])
users_router = APIRouter(prefix="/users", tags=["users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# =============================================================================
# Pydantic models for request/response validation
# Selon CDC Section 3 - Gestion des Utilisateurs (USR-01 à USR-13)
# =============================================================================


class RegisterRequest(BaseModel):
    """Requête d'inscription avec tous les champs CDC."""

    email: EmailStr
    password: str
    nom: str
    prenom: str
    role: Optional[str] = None
    type_utilisateur: Optional[str] = None
    telephone: Optional[str] = None
    metier: Optional[str] = None
    code_utilisateur: Optional[str] = None
    couleur: Optional[str] = None


class UpdateUserRequest(BaseModel):
    """Requête de mise à jour utilisateur."""

    nom: Optional[str] = None
    prenom: Optional[str] = None
    telephone: Optional[str] = None
    metier: Optional[str] = None
    couleur: Optional[str] = None
    photo_profil: Optional[str] = None
    contact_urgence_nom: Optional[str] = None
    contact_urgence_tel: Optional[str] = None
    role: Optional[str] = None
    type_utilisateur: Optional[str] = None
    code_utilisateur: Optional[str] = None


class UserResponse(BaseModel):
    """Réponse utilisateur complète selon CDC."""

    id: int
    email: str
    nom: str
    prenom: str
    nom_complet: str
    initiales: str
    role: str
    type_utilisateur: str
    is_active: bool
    couleur: str
    photo_profil: Optional[str]
    code_utilisateur: Optional[str]
    telephone: Optional[str]
    metier: Optional[str]
    contact_urgence_nom: Optional[str]
    contact_urgence_tel: Optional[str]
    created_at: datetime


class UserListResponse(BaseModel):
    """Réponse liste utilisateurs paginée (USR-09)."""

    users: List[UserResponse]
    total: int
    skip: int
    limit: int
    has_next: bool
    has_previous: bool


class AuthResponse(BaseModel):
    """Réponse d'authentification."""

    user: UserResponse
    access_token: str
    token_type: str


# =============================================================================
# Routes d'authentification
# =============================================================================


@router.post("/login", response_model=AuthResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    controller: AuthController = Depends(get_auth_controller),
):
    """
    Authentifie un utilisateur et retourne un token JWT.

    Args:
        form_data: Email (username) et mot de passe.
        controller: Controller d'authentification.

    Returns:
        Token d'accès et informations utilisateur.

    Raises:
        HTTPException 401: Identifiants invalides ou compte désactivé.
    """
    try:
        result = controller.login(form_data.username, form_data.password)
        return result
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except UserInactiveError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(
    request: RegisterRequest,
    controller: AuthController = Depends(get_auth_controller),
):
    """
    Inscrit un nouvel utilisateur (USR-01).

    Args:
        request: Données d'inscription.
        controller: Controller d'authentification.

    Returns:
        Token d'accès et informations utilisateur.

    Raises:
        HTTPException 400: Email/code déjà utilisé ou mot de passe faible.
    """
    try:
        result = controller.register(
            email=request.email,
            password=request.password,
            nom=request.nom,
            prenom=request.prenom,
            role=request.role,
            type_utilisateur=request.type_utilisateur,
            telephone=request.telephone,
            metier=request.metier,
            code_utilisateur=request.code_utilisateur,
            couleur=request.couleur,
        )
        return result
    except EmailAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except CodeAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except WeakPasswordError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/me", response_model=UserResponse)
def get_current_user(
    user_id: int = Depends(get_current_user_id),
    controller: AuthController = Depends(get_auth_controller),
):
    """
    Récupère l'utilisateur connecté.

    Args:
        user_id: ID de l'utilisateur (extrait du token).
        controller: Controller d'authentification.

    Returns:
        Informations de l'utilisateur connecté.

    Raises:
        HTTPException 401: Token invalide.
        HTTPException 404: Utilisateur non trouvé.
    """
    try:
        return controller.get_user_by_id(user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


# =============================================================================
# Routes de gestion des utilisateurs
# =============================================================================


@users_router.get("", response_model=UserListResponse)
def list_users(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limit: int = Query(20, ge=1, le=100, description="Nombre d'éléments par page"),
    role: Optional[str] = Query(None, description="Filtrer par rôle"),
    type_utilisateur: Optional[str] = Query(None, description="Filtrer par type"),
    active_only: bool = Query(False, description="Uniquement les utilisateurs actifs"),
    controller: AuthController = Depends(get_auth_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Liste les utilisateurs avec pagination (USR-09).

    Args:
        skip: Offset pour la pagination.
        limit: Limite d'éléments retournés.
        role: Filtrer par rôle (optionnel).
        type_utilisateur: Filtrer par type (optionnel).
        active_only: Filtrer sur les actifs uniquement.
        controller: Controller d'authentification.
        current_user_id: ID de l'utilisateur connecté (pour vérifier les permissions).

    Returns:
        Liste paginée des utilisateurs.
    """
    result = controller.list_users(
        skip=skip,
        limit=limit,
        role=role,
        type_utilisateur=type_utilisateur,
        active_only=active_only,
    )
    return result


@users_router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    controller: AuthController = Depends(get_auth_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Récupère un utilisateur par son ID.

    Args:
        user_id: ID de l'utilisateur.
        controller: Controller d'authentification.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Informations de l'utilisateur.

    Raises:
        HTTPException 404: Utilisateur non trouvé.
    """
    try:
        return controller.get_user_by_id(user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@users_router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    request: UpdateUserRequest,
    controller: AuthController = Depends(get_auth_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Met à jour un utilisateur.

    Args:
        user_id: ID de l'utilisateur à mettre à jour.
        request: Données de mise à jour.
        controller: Controller d'authentification.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Utilisateur mis à jour.

    Raises:
        HTTPException 404: Utilisateur non trouvé.
        HTTPException 400: Données invalides.
    """
    try:
        return controller.update_user(
            user_id=user_id,
            nom=request.nom,
            prenom=request.prenom,
            telephone=request.telephone,
            metier=request.metier,
            couleur=request.couleur,
            photo_profil=request.photo_profil,
            contact_urgence_nom=request.contact_urgence_nom,
            contact_urgence_tel=request.contact_urgence_tel,
            role=request.role,
            type_utilisateur=request.type_utilisateur,
            code_utilisateur=request.code_utilisateur,
        )
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except CodeAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@users_router.post("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(
    user_id: int,
    controller: AuthController = Depends(get_auth_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Désactive un utilisateur (USR-10 - révocation instantanée).

    Les données historiques sont conservées.

    Args:
        user_id: ID de l'utilisateur à désactiver.
        controller: Controller d'authentification.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Utilisateur désactivé.

    Raises:
        HTTPException 404: Utilisateur non trouvé.
    """
    try:
        return controller.deactivate_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@users_router.post("/{user_id}/activate", response_model=UserResponse)
def activate_user(
    user_id: int,
    controller: AuthController = Depends(get_auth_controller),
    current_user_id: int = Depends(get_current_user_id),
):
    """
    Réactive un utilisateur précédemment désactivé.

    Args:
        user_id: ID de l'utilisateur à activer.
        controller: Controller d'authentification.
        current_user_id: ID de l'utilisateur connecté.

    Returns:
        Utilisateur activé.

    Raises:
        HTTPException 404: Utilisateur non trouvé.
    """
    try:
        return controller.activate_user(user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
