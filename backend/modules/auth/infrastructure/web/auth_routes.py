"""Routes FastAPI pour l'authentification."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional

from ...adapters.controllers import AuthController
from ...application.use_cases import (
    InvalidCredentialsError,
    UserInactiveError,
    EmailAlreadyExistsError,
    WeakPasswordError,
    InvalidTokenError,
    UserNotFoundError,
)
from .dependencies import get_auth_controller, get_current_user_id

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# Pydantic models for request/response validation
class RegisterRequest(BaseModel):
    """Requête d'inscription."""

    email: EmailStr
    password: str
    nom: str
    prenom: str
    role: Optional[str] = None


class UserResponse(BaseModel):
    """Réponse utilisateur."""

    id: int
    email: str
    nom: str
    prenom: str
    role: str
    is_active: bool


class AuthResponse(BaseModel):
    """Réponse d'authentification."""

    user: UserResponse
    access_token: str
    token_type: str


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
    Inscrit un nouvel utilisateur.

    Args:
        request: Données d'inscription.
        controller: Controller d'authentification.

    Returns:
        Token d'accès et informations utilisateur.

    Raises:
        HTTPException 400: Email déjà utilisé ou mot de passe faible.
    """
    try:
        result = controller.register(
            email=request.email,
            password=request.password,
            nom=request.nom,
            prenom=request.prenom,
            role=request.role,
        )
        return result
    except EmailAlreadyExistsError as e:
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
