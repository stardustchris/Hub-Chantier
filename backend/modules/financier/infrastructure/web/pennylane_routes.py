"""Routes FastAPI pour l'integration Pennylane Inbound.

CONN-10: Sync factures fournisseurs.
CONN-11: Sync encaissements clients.
CONN-12: Import fournisseurs.
CONN-14: Gestion mappings analytiques.
CONN-15: Dashboard reconciliation.
"""

import logging
from datetime import datetime
from typing import Optional, Literal, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from sqlalchemy.orm import Session

from shared.infrastructure.database import get_db
from shared.infrastructure.web import (
    get_current_user_id,
    require_admin,
    require_conducteur_or_admin,
)

from ...application.dtos import (
    PennylaneSyncResultDTO,
    PennylaneSyncHistoryDTO,
    PennylanePendingReconciliationDTO,
    PennylaneMappingDTO,
    CreateMappingDTO,
    ResolveReconciliationDTO,
)
from ...application.use_cases.pennylane_sync_use_cases import (
    PennylaneSyncError,
    ReconciliationNotFoundError,
    ReconciliationAlreadyResolvedError,
    MappingCodeExistsError,
    MappingNotFoundError,
    AchatNotFoundError,
)
from .pennylane_dependencies import (
    get_sync_supplier_invoices_use_case,
    get_sync_customer_invoices_use_case,
    get_sync_suppliers_use_case,
    get_pending_reconciliations_use_case,
    get_resolve_reconciliation_use_case,
    get_mappings_use_case,
    get_create_mapping_use_case,
    get_delete_mapping_use_case,
    get_sync_history_use_case,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pennylane", tags=["pennylane"])


# ─────────────────────────────────────────────────────────────────────────────
# Request/Response Models
# ─────────────────────────────────────────────────────────────────────────────

class TriggerSyncRequest(BaseModel):
    """Request pour declencher une synchronisation."""

    sync_type: Literal["supplier_invoices", "customer_invoices", "suppliers", "all"] = Field(
        ...,
        description="Type de synchronisation a effectuer",
    )
    updated_since: Optional[datetime] = Field(
        None,
        description="Date depuis laquelle synchroniser (optionnel)",
    )


class TriggerSyncResponse(BaseModel):
    """Response apres declenchement d'une synchronisation."""

    success: bool
    results: List[dict]
    message: str


class ResolveReconciliationRequest(BaseModel):
    """Request pour resoudre une reconciliation."""

    action: Literal["match", "reject", "manual"] = Field(
        ...,
        description="Action: match (valider), reject (rejeter), manual (creer manuellement)",
    )
    achat_id: Optional[int] = Field(
        None,
        description="ID de l'achat a matcher (requis si action=match)",
    )


class CreateMappingRequest(BaseModel):
    """Request pour creer un mapping analytique."""

    code_analytique: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Code analytique Pennylane (ex: MONTMELIAN)",
    )
    chantier_id: int = Field(
        ...,
        gt=0,
        description="ID du chantier Hub Chantier",
    )


class PendingReconciliationResponse(BaseModel):
    """Response pour une reconciliation."""

    id: int
    pennylane_invoice_id: str
    supplier_name: Optional[str]
    supplier_siret: Optional[str]
    amount_ht: Optional[str]
    code_analytique: Optional[str]
    invoice_date: Optional[str]
    suggested_achat_id: Optional[int]
    suggested_achat_info: Optional[dict]
    status: str
    resolved_by: Optional[int]
    resolved_at: Optional[str]
    created_at: Optional[str]
    ecart_pct: Optional[float]


class MappingResponse(BaseModel):
    """Response pour un mapping analytique."""

    id: int
    code_analytique: str
    chantier_id: int
    chantier_nom: Optional[str]
    created_at: Optional[str]
    created_by: Optional[int]


class SyncHistoryResponse(BaseModel):
    """Response pour l'historique de sync."""

    id: int
    sync_type: str
    status: str
    records_processed: int
    records_created: int
    records_updated: int
    records_pending: int
    error_message: Optional[str]
    duration_seconds: Optional[float]
    started_at: str
    completed_at: Optional[str]


# ─────────────────────────────────────────────────────────────────────────────
# Pagination Response Models (alignement frontend)
# ─────────────────────────────────────────────────────────────────────────────

class PaginatedReconciliationResponse(BaseModel):
    """Response paginee pour les reconciliations."""

    items: List[PendingReconciliationResponse]
    total: int


class PaginatedMappingResponse(BaseModel):
    """Response paginee pour les mappings."""

    items: List[MappingResponse]
    total: int


class PaginatedSyncHistoryResponse(BaseModel):
    """Response paginee pour l'historique de sync."""

    items: List[SyncHistoryResponse]
    total: int


# ─────────────────────────────────────────────────────────────────────────────
# CONN-10/11/12: Synchronisation
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/sync",
    response_model=TriggerSyncResponse,
    status_code=status.HTTP_200_OK,
    summary="Declencher une synchronisation Pennylane",
    description="""
    Declenche une synchronisation manuelle avec Pennylane.

    Types de synchronisation:
    - supplier_invoices: Import des factures fournisseurs payees (CONN-10)
    - customer_invoices: Import des encaissements clients (CONN-11)
    - suppliers: Import/mise a jour des fournisseurs (CONN-12)
    - all: Execute les 3 synchronisations

    Requiert le role ADMIN ou CONDUCTEUR.
    """,
)
async def trigger_sync(
    request: TriggerSyncRequest,
    user_id: int = Depends(get_current_user_id),
    _: None = Depends(require_conducteur_or_admin),
    sync_supplier_use_case=Depends(get_sync_supplier_invoices_use_case),
    sync_customer_use_case=Depends(get_sync_customer_invoices_use_case),
    sync_suppliers_use_case=Depends(get_sync_suppliers_use_case),
):
    """Declenche une synchronisation Pennylane."""
    results = []
    errors = []

    try:
        if request.sync_type in ("supplier_invoices", "all"):
            result = await sync_supplier_use_case.execute(
                updated_since=request.updated_since,
            )
            results.append(result.to_dict())

        if request.sync_type in ("customer_invoices", "all"):
            result = await sync_customer_use_case.execute(
                updated_since=request.updated_since,
            )
            results.append(result.to_dict())

        if request.sync_type in ("suppliers", "all"):
            result = await sync_suppliers_use_case.execute()
            results.append(result.to_dict())

        total_processed = sum(r.get("records_processed", 0) for r in results)
        total_updated = sum(r.get("records_updated", 0) for r in results)
        total_pending = sum(r.get("records_pending", 0) for r in results)

        return TriggerSyncResponse(
            success=True,
            results=results,
            message=(
                f"Synchronisation terminee: {total_processed} traites, "
                f"{total_updated} mis a jour, {total_pending} en attente"
            ),
        )

    except PennylaneSyncError as e:
        logger.error(f"Erreur sync Pennylane: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Erreur synchronisation Pennylane: {e.message}",
        )


# ─────────────────────────────────────────────────────────────────────────────
# CONN-15: Reconciliations
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/pending",
    response_model=PaginatedReconciliationResponse,
    summary="Liste des reconciliations en attente",
    description="""
    Recupere la liste des factures Pennylane en attente de reconciliation.

    Filtrable par statut:
    - pending: En attente de validation
    - matched: Matche avec un achat
    - rejected: Rejetee
    - manual: A creer manuellement

    Requiert le role ADMIN ou CONDUCTEUR.
    """,
)
def get_pending_reconciliations(
    status_filter: Optional[str] = Query(
        None,
        alias="status",
        description="Filtrer par statut (pending, matched, rejected, manual)",
    ),
    limit: int = Query(50, ge=1, le=200, description="Nombre max de resultats"),
    offset: int = Query(0, ge=0, description="Offset pour pagination"),
    user_id: int = Depends(get_current_user_id),
    _: None = Depends(require_conducteur_or_admin),
    use_case=Depends(get_pending_reconciliations_use_case),
):
    """Recupere les reconciliations en attente."""
    dtos = use_case.execute(
        status=status_filter,
        limit=limit,
        offset=offset,
    )
    items = [dto.to_dict() for dto in dtos]
    # Note: Pour une pagination complete, le use_case devrait retourner le total
    # Pour l'instant, on utilise len(items) comme approximation
    return PaginatedReconciliationResponse(items=items, total=len(items))


@router.post(
    "/reconcile/{reconciliation_id}",
    response_model=PendingReconciliationResponse,
    summary="Resoudre une reconciliation",
    description="""
    Resout une reconciliation en attente.

    Actions possibles:
    - match: Valide le match avec un achat (achat_id requis)
    - reject: Rejette la facture (pas de correspondance)
    - manual: Marque pour creation manuelle d'un achat

    Requiert le role ADMIN ou CONDUCTEUR.
    """,
)
def resolve_reconciliation(
    reconciliation_id: int,
    request: ResolveReconciliationRequest,
    user_id: int = Depends(get_current_user_id),
    _: None = Depends(require_conducteur_or_admin),
    use_case=Depends(get_resolve_reconciliation_use_case),
):
    """Resout une reconciliation."""
    try:
        dto = ResolveReconciliationDTO(
            reconciliation_id=reconciliation_id,
            action=request.action,
            achat_id=request.achat_id,
        )

        result = use_case.execute(dto, user_id)
        return result.to_dict()

    except ReconciliationNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ReconciliationAlreadyResolvedError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except AchatNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ─────────────────────────────────────────────────────────────────────────────
# CONN-14: Mappings analytiques
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/mappings",
    response_model=PaginatedMappingResponse,
    summary="Liste des mappings analytiques",
    description="""
    Recupere la liste des correspondances entre codes analytiques Pennylane
    et chantiers Hub Chantier.

    Requiert le role ADMIN ou CONDUCTEUR.
    """,
)
def get_mappings(
    user_id: int = Depends(get_current_user_id),
    _: None = Depends(require_conducteur_or_admin),
    use_case=Depends(get_mappings_use_case),
):
    """Recupere les mappings analytiques."""
    dtos = use_case.execute()
    items = [dto.to_dict() for dto in dtos]
    return PaginatedMappingResponse(items=items, total=len(items))


@router.post(
    "/mappings",
    response_model=MappingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Creer un mapping analytique",
    description="""
    Cree une nouvelle correspondance entre un code analytique Pennylane
    et un chantier Hub Chantier.

    Le code analytique doit etre unique.

    Requiert le role ADMIN.
    """,
)
def create_mapping(
    request: CreateMappingRequest,
    user_id: int = Depends(get_current_user_id),
    _: None = Depends(require_admin),
    use_case=Depends(get_create_mapping_use_case),
):
    """Cree un mapping analytique."""
    try:
        dto = CreateMappingDTO(
            code_analytique=request.code_analytique,
            chantier_id=request.chantier_id,
        )

        result = use_case.execute(dto, user_id)
        return result.to_dict()

    except MappingCodeExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.delete(
    "/mappings/{mapping_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un mapping analytique",
    description="""
    Supprime une correspondance code analytique -> chantier.

    Requiert le role ADMIN.
    """,
)
def delete_mapping(
    mapping_id: int,
    user_id: int = Depends(get_current_user_id),
    _: None = Depends(require_admin),
    use_case=Depends(get_delete_mapping_use_case),
):
    """Supprime un mapping analytique."""
    try:
        use_case.execute(mapping_id)

    except MappingNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# ─────────────────────────────────────────────────────────────────────────────
# Historique des synchronisations
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/sync-history",
    response_model=PaginatedSyncHistoryResponse,
    summary="Historique des synchronisations",
    description="""
    Recupere l'historique des synchronisations Pennylane.

    Filtrable par type de synchronisation.

    Requiert le role ADMIN ou CONDUCTEUR.
    """,
)
def get_sync_history(
    sync_type: Optional[str] = Query(
        None,
        description="Filtrer par type (supplier_invoices, customer_invoices, suppliers)",
    ),
    limit: int = Query(20, ge=1, le=100, description="Nombre max de resultats"),
    offset: int = Query(0, ge=0, description="Offset pour pagination"),
    user_id: int = Depends(get_current_user_id),
    _: None = Depends(require_conducteur_or_admin),
    use_case=Depends(get_sync_history_use_case),
):
    """Recupere l'historique des synchronisations."""
    dtos = use_case.execute(
        sync_type=sync_type,
        limit=limit,
        offset=offset,
    )
    items = [dto.to_dict() for dto in dtos]
    return PaginatedSyncHistoryResponse(items=items, total=len(items))
