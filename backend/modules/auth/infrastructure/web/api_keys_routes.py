"""Routes FastAPI pour la gestion des clés API."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from shared.infrastructure.database import get_db
from modules.auth.infrastructure.web.dependencies import get_current_user
from modules.auth.infrastructure.persistence.user_model import UserModel

# Use Cases
from ...application.use_cases.create_api_key import CreateAPIKeyUseCase
from ...application.use_cases.list_api_keys import ListAPIKeysUseCase
from ...application.use_cases.revoke_api_key import (
    RevokeAPIKeyUseCase,
    APIKeyNotFoundError,
    UnauthorizedRevokeError,
)

# DTOs
from ...application.dtos.api_key_dtos import CreateAPIKeyDTO, RevokeAPIKeyDTO

# Repository
from ...infrastructure.persistence.sqlalchemy_api_key_repository import (
    SQLAlchemyAPIKeyRepository,
)


router = APIRouter(prefix="/api-keys", tags=["API Keys"])


# --- Pydantic Models (Request/Response) ---


class CreateAPIKeyRequest(BaseModel):
    """Requête de création d'une clé API."""

    nom: str = Field(..., min_length=1, max_length=255, description="Nom de la clé")
    description: str | None = Field(None, description="Description détaillée")
    scopes: List[str] = Field(
        default=["read"], description="Permissions (read, write, admin)"
    )
    expires_days: int | None = Field(
        default=90, ge=1, le=3650, description="Jours avant expiration (1-3650)"
    )


class CreateAPIKeyResponse(BaseModel):
    """Réponse après création d'une clé API."""

    api_key: str = Field(
        ..., description="SECRET - Afficher UNE FOIS et copier dans presse-papier"
    )
    key_id: str
    key_prefix: str
    nom: str
    created_at: str
    expires_at: str | None


class APIKeyInfoResponse(BaseModel):
    """Informations d'une clé API (sans secret)."""

    id: str
    key_prefix: str
    nom: str
    description: str | None
    scopes: List[str]
    rate_limit_per_hour: int
    is_active: bool
    last_used_at: str | None
    expires_at: str | None
    created_at: str


# --- Routes ---


@router.post(
    "",
    response_model=CreateAPIKeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer une nouvelle clé API",
    description="""
    Crée une nouvelle clé API pour l'utilisateur authentifié.

    **IMPORTANT**: Le secret (api_key) est retourné UNE SEULE FOIS.
    Il ne pourra plus jamais être récupéré après cette réponse.

    L'utilisateur doit le copier immédiatement et le stocker de manière sécurisée.
    """,
)
async def create_api_key(
    request: CreateAPIKeyRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Crée une nouvelle clé API.

    Args:
        request: Données de création
        current_user: Utilisateur authentifié (JWT)
        db: Session database

    Returns:
        Secret + infos clé (secret affiché UNE FOIS)
    """
    # Créer DTO
    dto = CreateAPIKeyDTO(
        user_id=current_user.id,
        nom=request.nom,
        description=request.description,
        scopes=request.scopes,
        expires_days=request.expires_days,
    )

    # Use Case
    repo = SQLAlchemyAPIKeyRepository(db)
    use_case = CreateAPIKeyUseCase(repo)

    try:
        result = use_case.execute(dto)

        return CreateAPIKeyResponse(
            api_key=result.api_key,
            key_id=str(result.key_id),
            key_prefix=result.key_prefix,
            nom=result.nom,
            created_at=result.created_at.isoformat(),
            expires_at=result.expires_at.isoformat() if result.expires_at else None,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur création clé: {str(e)}")


@router.get(
    "",
    response_model=List[APIKeyInfoResponse],
    summary="Lister mes clés API",
    description="Liste toutes les clés API actives de l'utilisateur authentifié.",
)
async def list_api_keys(
    include_revoked: bool = False,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Liste les clés API de l'utilisateur.

    Args:
        include_revoked: Inclure les clés révoquées (défaut: False)
        current_user: Utilisateur authentifié
        db: Session database

    Returns:
        Liste des clés (sans secrets)
    """
    # Use Case
    repo = SQLAlchemyAPIKeyRepository(db)
    use_case = ListAPIKeysUseCase(repo)

    try:
        api_keys = use_case.execute(
            user_id=current_user.id, include_revoked=include_revoked
        )

        return [
            APIKeyInfoResponse(
                id=str(key.id),
                key_prefix=key.key_prefix,
                nom=key.nom,
                description=key.description,
                scopes=key.scopes,
                rate_limit_per_hour=key.rate_limit_per_hour,
                is_active=key.is_active,
                last_used_at=key.last_used_at.isoformat() if key.last_used_at else None,
                expires_at=key.expires_at.isoformat() if key.expires_at else None,
                created_at=key.created_at.isoformat(),
            )
            for key in api_keys
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur listing clés: {str(e)}")


@router.delete(
    "/{key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Révoquer une clé API",
    description="""
    Révoque (désactive) une clé API.

    La clé ne pourra plus être utilisée pour l'authentification.
    L'historique est conservé pour l'audit.
    """,
)
async def revoke_api_key(
    key_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Révoque une clé API.

    Args:
        key_id: UUID de la clé à révoquer
        current_user: Utilisateur authentifié
        db: Session database

    Raises:
        404: Si clé non trouvée
        403: Si l'utilisateur n'est pas propriétaire
    """
    # Use Case
    repo = SQLAlchemyAPIKeyRepository(db)
    use_case = RevokeAPIKeyUseCase(repo)

    dto = RevokeAPIKeyDTO(api_key_id=key_id, user_id=current_user.id)

    try:
        use_case.execute(dto)
        return None  # 204 No Content

    except APIKeyNotFoundError:
        raise HTTPException(status_code=404, detail="Clé API non trouvée")

    except UnauthorizedRevokeError:
        raise HTTPException(
            status_code=403, detail="Vous n'êtes pas propriétaire de cette clé"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur révocation clé: {str(e)}")
