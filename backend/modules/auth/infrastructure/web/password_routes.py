"""Routes FastAPI pour la gestion des mots de passe et invitations."""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from shared.infrastructure.database import get_db
from shared.infrastructure.password_hasher import PasswordHasher
from ...application.use_cases.request_password_reset import RequestPasswordResetUseCase
from ...application.use_cases.reset_password import ResetPasswordUseCase
from ...application.use_cases.change_password import ChangePasswordUseCase
from ...application.use_cases.invite_user import InviteUserUseCase
from ...application.use_cases.accept_invitation import AcceptInvitationUseCase
from ...infrastructure.persistence.sqlalchemy_user_repository import SQLAlchemyUserRepository
from ...domain.exceptions import (
    InvalidResetTokenError,
    InvalidInvitationTokenError,
    WeakPasswordError,
    InvalidCredentialsError,
    UserNotFoundError,
    EmailAlreadyExistsError,
    CodeAlreadyExistsError,
)
from ...domain.value_objects import Role, TypeUtilisateur
from .dependencies import get_current_user_id, require_admin_or_conducteur

router = APIRouter(prefix="/auth", tags=["auth", "password"])


# =============================================================================
# Pydantic models for request/response validation
# =============================================================================


class RequestPasswordResetRequest(BaseModel):
    """Requête de demande de réinitialisation de mot de passe."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Requête de réinitialisation de mot de passe avec token."""

    token: str
    new_password: str


class ChangePasswordRequest(BaseModel):
    """Requête de changement de mot de passe."""

    old_password: str
    new_password: str


class InviteUserRequest(BaseModel):
    """Requête d'invitation d'un utilisateur."""

    email: EmailStr
    nom: str
    prenom: str
    role: str
    type_utilisateur: str = "EMPLOYE"
    code_utilisateur: str | None = None
    metier: str | None = None


class AcceptInvitationRequest(BaseModel):
    """Requête d'acceptation d'invitation."""

    token: str
    password: str


class MessageResponse(BaseModel):
    """Réponse simple avec message."""

    message: str


# =============================================================================
# Factories pour les use cases
# =============================================================================


def get_password_hasher() -> PasswordHasher:
    """Factory pour le service de hachage de mot de passe."""
    return PasswordHasher()


def get_request_password_reset_use_case(
    db: Session = Depends(get_db),
) -> RequestPasswordResetUseCase:
    """Factory pour RequestPasswordResetUseCase."""
    user_repository = SQLAlchemyUserRepository(db)
    return RequestPasswordResetUseCase(user_repository)


def get_reset_password_use_case(
    db: Session = Depends(get_db),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
) -> ResetPasswordUseCase:
    """Factory pour ResetPasswordUseCase."""
    user_repository = SQLAlchemyUserRepository(db)
    return ResetPasswordUseCase(user_repository, password_hasher)


def get_change_password_use_case(
    db: Session = Depends(get_db),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
) -> ChangePasswordUseCase:
    """Factory pour ChangePasswordUseCase."""
    user_repository = SQLAlchemyUserRepository(db)
    return ChangePasswordUseCase(user_repository, password_hasher)


def get_invite_user_use_case(
    db: Session = Depends(get_db),
) -> InviteUserUseCase:
    """Factory pour InviteUserUseCase."""
    user_repository = SQLAlchemyUserRepository(db)
    return InviteUserUseCase(user_repository)


def get_accept_invitation_use_case(
    db: Session = Depends(get_db),
    password_hasher: PasswordHasher = Depends(get_password_hasher),
) -> AcceptInvitationUseCase:
    """Factory pour AcceptInvitationUseCase."""
    user_repository = SQLAlchemyUserRepository(db)
    return AcceptInvitationUseCase(user_repository, password_hasher)


# =============================================================================
# Routes Password Reset
# =============================================================================


@router.post("/request-password-reset", response_model=MessageResponse, status_code=status.HTTP_200_OK)
def request_password_reset(
    request_data: RequestPasswordResetRequest,
    use_case: RequestPasswordResetUseCase = Depends(get_request_password_reset_use_case),
):
    """
    Demande une réinitialisation de mot de passe.

    Envoie un email avec un lien de réinitialisation si l'utilisateur existe.
    Retourne toujours succès pour éviter l'énumération des comptes.

    Args:
        request_data: Email de l'utilisateur.
        use_case: Use case de demande de réinitialisation.

    Returns:
        Message de confirmation.
    """
    use_case.execute(request_data.email)

    return MessageResponse(
        message="Si cette adresse email existe, un email de réinitialisation a été envoyé."
    )


@router.post("/reset-password", response_model=MessageResponse, status_code=status.HTTP_200_OK)
def reset_password(
    request_data: ResetPasswordRequest,
    use_case: ResetPasswordUseCase = Depends(get_reset_password_use_case),
):
    """
    Réinitialise le mot de passe avec un token.

    Args:
        request_data: Token et nouveau mot de passe.
        use_case: Use case de réinitialisation.

    Returns:
        Message de confirmation.

    Raises:
        HTTPException 400: Token invalide ou expiré, ou mot de passe trop faible.
    """
    try:
        use_case.execute(request_data.token, request_data.new_password)
        return MessageResponse(message="Mot de passe réinitialisé avec succès")

    except InvalidResetTokenError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except WeakPasswordError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# =============================================================================
# Routes Change Password
# =============================================================================


@router.post("/change-password", response_model=MessageResponse, status_code=status.HTTP_200_OK)
def change_password(
    request_data: ChangePasswordRequest,
    current_user_id: int = Depends(get_current_user_id),
    use_case: ChangePasswordUseCase = Depends(get_change_password_use_case),
):
    """
    Change le mot de passe de l'utilisateur connecté.

    Nécessite une authentification (JWT token).

    Args:
        request_data: Ancien et nouveau mot de passe.
        current_user_id: ID de l'utilisateur connecté (depuis JWT).
        use_case: Use case de changement de mot de passe.

    Returns:
        Message de confirmation.

    Raises:
        HTTPException 400: Ancien mot de passe incorrect ou nouveau mot de passe trop faible.
        HTTPException 404: Utilisateur non trouvé.
    """
    try:
        use_case.execute(
            user_id=current_user_id,
            old_password=request_data.old_password,
            new_password=request_data.new_password,
        )
        return MessageResponse(message="Mot de passe modifié avec succès")

    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidCredentialsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except WeakPasswordError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# =============================================================================
# Routes Invitation
# =============================================================================


@router.post("/invite-user", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def invite_user(
    request_data: InviteUserRequest,
    current_user_id: int = Depends(require_admin_or_conducteur),
    use_case: InviteUserUseCase = Depends(get_invite_user_use_case),
):
    """
    Invite un nouvel utilisateur (Admin ou Conducteur uniquement).

    Crée un compte pré-rempli et envoie un email d'invitation.

    Args:
        request_data: Données de l'invitation.
        current_user_id: ID de l'utilisateur qui invite (Admin/Conducteur).
        use_case: Use case d'invitation.

    Returns:
        Message de confirmation.

    Raises:
        HTTPException 400: Email ou code utilisateur déjà existant.
        HTTPException 403: Rôle insuffisant.
    """
    try:
        # Convertir les strings en enums
        role = Role.from_string(request_data.role)
        type_utilisateur = TypeUtilisateur.from_string(request_data.type_utilisateur)

        use_case.execute(
            email=request_data.email,
            nom=request_data.nom,
            prenom=request_data.prenom,
            role=role,
            type_utilisateur=type_utilisateur,
            code_utilisateur=request_data.code_utilisateur,
            metier=request_data.metier,
            inviter_name="Un administrateur",  # TODO: Récupérer le nom de l'inviteur
        )

        return MessageResponse(
            message=f"Invitation envoyée avec succès à {request_data.email}"
        )

    except EmailAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except CodeAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/accept-invitation", response_model=MessageResponse, status_code=status.HTTP_200_OK)
def accept_invitation(
    request_data: AcceptInvitationRequest,
    use_case: AcceptInvitationUseCase = Depends(get_accept_invitation_use_case),
):
    """
    Accepte une invitation et active le compte.

    L'utilisateur définit son mot de passe et le compte est activé.

    Args:
        request_data: Token d'invitation et mot de passe choisi.
        use_case: Use case d'acceptation d'invitation.

    Returns:
        Message de confirmation.

    Raises:
        HTTPException 400: Token invalide/expiré ou mot de passe trop faible.
    """
    try:
        use_case.execute(request_data.token, request_data.password)
        return MessageResponse(
            message="Compte activé avec succès. Vous pouvez maintenant vous connecter."
        )

    except InvalidInvitationTokenError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except WeakPasswordError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
