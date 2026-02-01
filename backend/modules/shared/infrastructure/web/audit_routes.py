"""Routes FastAPI pour le module Audit."""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field

from ...application.services.audit_service import AuditService, AuditServiceError
from ...application.dtos.audit_dtos import AuditEntryDTO, AuditHistoryResponseDTO
from .dependencies import get_audit_service


router = APIRouter(prefix="/audit", tags=["audit"])


# ──────────────────────────────────────────────────────────────────────────────
# Pydantic Models pour les requêtes/réponses
# ──────────────────────────────────────────────────────────────────────────────


class AuditEntryResponse(BaseModel):
    """Modèle de réponse pour une entrée d'audit."""

    id: str
    entity_type: str
    entity_id: str
    action: str
    field_name: Optional[str]
    old_value: Optional[str]
    new_value: Optional[str]
    author_id: int
    author_name: str
    timestamp: datetime
    motif: Optional[str]
    metadata: Optional[dict]

    class Config:
        from_attributes = True


class AuditHistoryResponse(BaseModel):
    """Modèle de réponse pour l'historique d'audit."""

    entries: List[AuditEntryResponse]
    total: int
    limit: int
    offset: int
    has_more: bool


# ──────────────────────────────────────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────────────────────────────────────


@router.get(
    "/history/{entity_type}/{entity_id}",
    response_model=AuditHistoryResponse,
    summary="Récupère l'historique d'une entité",
    description="""
    Récupère toutes les entrées d'audit pour une entité spécifique.

    Les résultats sont triés par date décroissante (plus récent en premier).
    Supporte la pagination via les paramètres `limit` et `offset`.

    **Exemples d'utilisation :**
    - `/audit/history/devis/123` - Historique du devis ID 123
    - `/audit/history/lot_budgetaire/456?limit=20` - 20 dernières entrées du lot 456
    """,
)
def get_entity_history(
    entity_type: str = Field(..., description="Type d'entité (ex: devis, lot_budgetaire)"),
    entity_id: str = Field(..., description="ID de l'entité"),
    limit: int = Query(50, ge=1, le=200, description="Nombre maximum d'entrées à retourner"),
    offset: int = Query(0, ge=0, description="Décalage pour pagination"),
    service: AuditService = Depends(get_audit_service),
):
    """
    Récupère l'historique d'une entité.

    Args:
        entity_type: Type de l'entité.
        entity_id: ID de l'entité.
        limit: Nombre maximum d'entrées à retourner.
        offset: Décalage pour pagination.
        service: Service d'audit injecté.

    Returns:
        AuditHistoryResponse contenant les entrées d'audit.

    Raises:
        HTTPException: En cas d'erreur.
    """
    try:
        result = service.get_history(
            entity_type=entity_type,
            entity_id=entity_id,
            limit=limit,
            offset=offset,
        )

        return AuditHistoryResponse(
            entries=[
                AuditEntryResponse(
                    id=entry.id,
                    entity_type=entry.entity_type,
                    entity_id=entry.entity_id,
                    action=entry.action,
                    field_name=entry.field_name,
                    old_value=entry.old_value,
                    new_value=entry.new_value,
                    author_id=entry.author_id,
                    author_name=entry.author_name,
                    timestamp=entry.timestamp,
                    motif=entry.motif,
                    metadata=entry.metadata,
                )
                for entry in result.entries
            ],
            total=result.total,
            limit=result.limit,
            offset=result.offset,
            has_more=result.has_more,
        )

    except AuditServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération de l'historique : {str(e)}",
        )


@router.get(
    "/user/{user_id}",
    response_model=List[AuditEntryResponse],
    summary="Récupère les actions d'un utilisateur",
    description="""
    Récupère toutes les actions effectuées par un utilisateur spécifique.

    Permet de filtrer par période et/ou type d'entité.
    Utile pour l'audit des actions utilisateur et la conformité RGPD.
    """,
)
def get_user_actions(
    user_id: int = Field(..., description="ID de l'utilisateur"),
    start_date: Optional[datetime] = Query(None, description="Date de début (ISO 8601)"),
    end_date: Optional[datetime] = Query(None, description="Date de fin (ISO 8601)"),
    entity_type: Optional[str] = Query(None, description="Filtrer par type d'entité"),
    limit: int = Query(100, ge=1, le=500, description="Nombre maximum d'entrées"),
    offset: int = Query(0, ge=0, description="Décalage pour pagination"),
    service: AuditService = Depends(get_audit_service),
):
    """
    Récupère les actions d'un utilisateur.

    Args:
        user_id: ID de l'utilisateur.
        start_date: Date de début (optionnel).
        end_date: Date de fin (optionnel).
        entity_type: Filtrer par type d'entité (optionnel).
        limit: Nombre maximum d'entrées.
        offset: Décalage pour pagination.
        service: Service d'audit injecté.

    Returns:
        Liste des AuditEntryResponse.

    Raises:
        HTTPException: En cas d'erreur.
    """
    try:
        entries = service.get_user_actions(
            author_id=user_id,
            start_date=start_date,
            end_date=end_date,
            entity_type=entity_type,
            limit=limit,
            offset=offset,
        )

        return [
            AuditEntryResponse(
                id=entry.id,
                entity_type=entry.entity_type,
                entity_id=entry.entity_id,
                action=entry.action,
                field_name=entry.field_name,
                old_value=entry.old_value,
                new_value=entry.new_value,
                author_id=entry.author_id,
                author_name=entry.author_name,
                timestamp=entry.timestamp,
                motif=entry.motif,
                metadata=entry.metadata,
            )
            for entry in entries
        ]

    except AuditServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des actions utilisateur : {str(e)}",
        )


@router.get(
    "/recent",
    response_model=List[AuditEntryResponse],
    summary="Récupère les entrées d'audit récentes",
    description="""
    Récupère les entrées d'audit les plus récentes.

    Utile pour afficher un feed d'activité global dans le dashboard.
    Permet de filtrer par type d'entité et/ou type d'action.
    """,
)
def get_recent_entries(
    entity_type: Optional[str] = Query(None, description="Filtrer par type d'entité"),
    action: Optional[str] = Query(None, description="Filtrer par type d'action"),
    limit: int = Query(50, ge=1, le=200, description="Nombre maximum d'entrées"),
    service: AuditService = Depends(get_audit_service),
):
    """
    Récupère les entrées d'audit récentes.

    Args:
        entity_type: Filtrer par type d'entité (optionnel).
        action: Filtrer par type d'action (optionnel).
        limit: Nombre maximum d'entrées.
        service: Service d'audit injecté.

    Returns:
        Liste des AuditEntryResponse.

    Raises:
        HTTPException: En cas d'erreur.
    """
    try:
        entries = service.get_recent_entries(
            entity_type=entity_type,
            action=action,
            limit=limit,
        )

        return [
            AuditEntryResponse(
                id=entry.id,
                entity_type=entry.entity_type,
                entity_id=entry.entity_id,
                action=entry.action,
                field_name=entry.field_name,
                old_value=entry.old_value,
                new_value=entry.new_value,
                author_id=entry.author_id,
                author_name=entry.author_name,
                timestamp=entry.timestamp,
                motif=entry.motif,
                metadata=entry.metadata,
            )
            for entry in entries
        ]

    except AuditServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des entrées récentes : {str(e)}",
        )


@router.get(
    "/search",
    response_model=AuditHistoryResponse,
    summary="Recherche avancée dans l'audit",
    description="""
    Recherche avancée permettant de combiner plusieurs critères.

    Tous les paramètres sont optionnels et peuvent être combinés.
    Supporte la pagination.
    """,
)
def search_audit(
    entity_type: Optional[str] = Query(None, description="Filtrer par type d'entité"),
    entity_id: Optional[str] = Query(None, description="Filtrer par ID d'entité"),
    action: Optional[str] = Query(None, description="Filtrer par type d'action"),
    author_id: Optional[int] = Query(None, description="Filtrer par auteur"),
    start_date: Optional[datetime] = Query(None, description="Date de début (ISO 8601)"),
    end_date: Optional[datetime] = Query(None, description="Date de fin (ISO 8601)"),
    limit: int = Query(100, ge=1, le=500, description="Nombre maximum d'entrées"),
    offset: int = Query(0, ge=0, description="Décalage pour pagination"),
    service: AuditService = Depends(get_audit_service),
):
    """
    Recherche avancée dans les entrées d'audit.

    Args:
        entity_type: Filtrer par type d'entité (optionnel).
        entity_id: Filtrer par ID d'entité (optionnel).
        action: Filtrer par type d'action (optionnel).
        author_id: Filtrer par auteur (optionnel).
        start_date: Date de début (optionnel).
        end_date: Date de fin (optionnel).
        limit: Nombre maximum d'entrées.
        offset: Décalage pour pagination.
        service: Service d'audit injecté.

    Returns:
        AuditHistoryResponse contenant les résultats.

    Raises:
        HTTPException: En cas d'erreur.
    """
    try:
        result = service.search(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            author_id=author_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )

        return AuditHistoryResponse(
            entries=[
                AuditEntryResponse(
                    id=entry.id,
                    entity_type=entry.entity_type,
                    entity_id=entry.entity_id,
                    action=entry.action,
                    field_name=entry.field_name,
                    old_value=entry.old_value,
                    new_value=entry.new_value,
                    author_id=entry.author_id,
                    author_name=entry.author_name,
                    timestamp=entry.timestamp,
                    motif=entry.motif,
                    metadata=entry.metadata,
                )
                for entry in result.entries
            ],
            total=result.total,
            limit=result.limit,
            offset=result.offset,
            has_more=result.has_more,
        )

    except AuditServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la recherche : {str(e)}",
        )
