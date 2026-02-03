"""DTOs pour la synchronisation Pennylane.

CONN-10: Sync factures fournisseurs.
CONN-11: Sync encaissements clients.
CONN-12: Import fournisseurs.
CONN-14: Gestion mappings analytiques.
CONN-15: Dashboard reconciliation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any, TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from ...domain.entities import (
        PennylaneSyncLog,
        PennylaneMappingAnalytique,
        PennylanePendingReconciliation,
    )
    from shared.infrastructure.connectors.pennylane.sync_service import SyncResult


# ─────────────────────────────────────────────────────────────────────────────
# DTOs de sortie
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PennylaneSyncResultDTO:
    """DTO pour le resultat d'une synchronisation Pennylane."""

    sync_id: int
    sync_type: str
    status: str
    records_processed: int
    records_created: int
    records_updated: int
    records_pending: int
    errors: List[str]
    duration_seconds: float
    started_at: str
    completed_at: str

    @classmethod
    def from_result(
        cls,
        result: "SyncResult",
        sync_id: int,
    ) -> "PennylaneSyncResultDTO":
        """Cree un DTO depuis un SyncResult."""
        status = "completed"
        if result.has_errors:
            status = "partial" if result.records_pending > 0 else "failed"

        return cls(
            sync_id=sync_id,
            sync_type=result.sync_type,
            status=status,
            records_processed=result.records_processed,
            records_created=result.records_created,
            records_updated=result.records_updated,
            records_pending=result.records_pending,
            errors=result.errors,
            duration_seconds=result.duration_seconds,
            started_at=result.started_at.isoformat(),
            completed_at=result.completed_at.isoformat(),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le DTO en dictionnaire."""
        return {
            "sync_id": self.sync_id,
            "sync_type": self.sync_type,
            "status": self.status,
            "records_processed": self.records_processed,
            "records_created": self.records_created,
            "records_updated": self.records_updated,
            "records_pending": self.records_pending,
            "errors": self.errors,
            "duration_seconds": self.duration_seconds,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


@dataclass
class PennylaneSyncHistoryDTO:
    """DTO pour l'historique des synchronisations."""

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

    @classmethod
    def from_entity(cls, log: "PennylaneSyncLog") -> "PennylaneSyncHistoryDTO":
        """Cree un DTO depuis une entite PennylaneSyncLog."""
        return cls(
            id=log.id,
            sync_type=log.sync_type,
            status=log.status,
            records_processed=log.records_processed,
            records_created=log.records_created,
            records_updated=log.records_updated,
            records_pending=log.records_pending,
            error_message=log.error_message,
            duration_seconds=log.duree_secondes,
            started_at=log.started_at.isoformat(),
            completed_at=log.completed_at.isoformat() if log.completed_at else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "sync_type": self.sync_type,
            "status": self.status,
            "records_processed": self.records_processed,
            "records_created": self.records_created,
            "records_updated": self.records_updated,
            "records_pending": self.records_pending,
            "error_message": self.error_message,
            "duration_seconds": self.duration_seconds,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


@dataclass
class PennylanePendingReconciliationDTO:
    """DTO pour une reconciliation en attente."""

    id: int
    pennylane_invoice_id: str
    supplier_name: Optional[str]
    supplier_siret: Optional[str]
    amount_ht: Optional[str]
    code_analytique: Optional[str]
    invoice_date: Optional[str]
    suggested_achat_id: Optional[int]
    suggested_achat_info: Optional[Dict[str, Any]]
    status: str
    resolved_by: Optional[int]
    resolved_at: Optional[str]
    created_at: Optional[str]
    # Calculs
    ecart_pct: Optional[float] = None

    @classmethod
    def from_entity(
        cls,
        pending: "PennylanePendingReconciliation",
        suggested_achat_info: Optional[Dict[str, Any]] = None,
    ) -> "PennylanePendingReconciliationDTO":
        """Cree un DTO depuis une entite PennylanePendingReconciliation."""
        # Calculer l'ecart si on a les infos de l'achat suggere
        ecart_pct = None
        if suggested_achat_info and pending.amount_ht:
            try:
                achat_montant = Decimal(suggested_achat_info.get("montant_ht", "0"))
                if achat_montant > 0:
                    ecart = abs(pending.amount_ht - achat_montant)
                    ecart_pct = float(ecart / achat_montant * 100)
            except (ValueError, TypeError):
                pass

        return cls(
            id=pending.id,
            pennylane_invoice_id=pending.pennylane_invoice_id,
            supplier_name=pending.supplier_name,
            supplier_siret=pending.supplier_siret,
            amount_ht=str(pending.amount_ht) if pending.amount_ht else None,
            code_analytique=pending.code_analytique,
            invoice_date=pending.invoice_date.isoformat() if pending.invoice_date else None,
            suggested_achat_id=pending.suggested_achat_id,
            suggested_achat_info=suggested_achat_info,
            status=pending.status,
            resolved_by=pending.resolved_by,
            resolved_at=pending.resolved_at.isoformat() if pending.resolved_at else None,
            created_at=pending.created_at.isoformat() if pending.created_at else None,
            ecart_pct=ecart_pct,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "pennylane_invoice_id": self.pennylane_invoice_id,
            "supplier_name": self.supplier_name,
            "supplier_siret": self.supplier_siret,
            "amount_ht": self.amount_ht,
            "code_analytique": self.code_analytique,
            "invoice_date": self.invoice_date,
            "suggested_achat_id": self.suggested_achat_id,
            "suggested_achat_info": self.suggested_achat_info,
            "status": self.status,
            "resolved_by": self.resolved_by,
            "resolved_at": self.resolved_at,
            "created_at": self.created_at,
            "ecart_pct": self.ecart_pct,
        }


@dataclass
class PennylaneMappingDTO:
    """DTO pour un mapping analytique."""

    id: int
    code_analytique: str
    chantier_id: int
    chantier_nom: Optional[str]
    created_at: Optional[str]
    created_by: Optional[int]

    @classmethod
    def from_entity(
        cls,
        mapping: "PennylaneMappingAnalytique",
        chantier_nom: Optional[str] = None,
    ) -> "PennylaneMappingDTO":
        """Cree un DTO depuis une entite PennylaneMappingAnalytique."""
        return cls(
            id=mapping.id,
            code_analytique=mapping.code_analytique,
            chantier_id=mapping.chantier_id,
            chantier_nom=chantier_nom,
            created_at=mapping.created_at.isoformat() if mapping.created_at else None,
            created_by=mapping.created_by,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "code_analytique": self.code_analytique,
            "chantier_id": self.chantier_id,
            "chantier_nom": self.chantier_nom,
            "created_at": self.created_at,
            "created_by": self.created_by,
        }


@dataclass
class PendingReconciliationListDTO:
    """DTO pour une liste paginee de reconciliations."""

    items: List[PennylanePendingReconciliationDTO]
    total: int
    pending_count: int
    matched_count: int
    rejected_count: int

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le DTO en dictionnaire."""
        return {
            "items": [item.to_dict() for item in self.items],
            "total": self.total,
            "pending_count": self.pending_count,
            "matched_count": self.matched_count,
            "rejected_count": self.rejected_count,
        }


# ─────────────────────────────────────────────────────────────────────────────
# DTOs d'entree
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class CreateMappingDTO:
    """DTO pour la creation d'un mapping analytique."""

    code_analytique: str
    chantier_id: int


@dataclass
class ResolveReconciliationDTO:
    """DTO pour la resolution d'une reconciliation."""

    reconciliation_id: int
    action: Literal["match", "reject", "manual"]
    achat_id: Optional[int] = None  # Requis si action == "match"


@dataclass
class TriggerSyncDTO:
    """DTO pour declencher une synchronisation manuelle."""

    sync_type: Literal["supplier_invoices", "customer_invoices", "suppliers", "all"]
    updated_since: Optional[datetime] = None


# ─────────────────────────────────────────────────────────────────────────────
# DTOs Dashboard
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PennylaneDashboardDTO:
    """DTO pour le dashboard Pennylane."""

    # Derniere synchronisation
    last_sync_supplier_invoices: Optional[PennylaneSyncHistoryDTO]
    last_sync_customer_invoices: Optional[PennylaneSyncHistoryDTO]
    last_sync_suppliers: Optional[PennylaneSyncHistoryDTO]

    # Compteurs reconciliation
    pending_count: int
    matched_today_count: int

    # Stats globales
    total_imported_invoices: int
    total_matched_invoices: int
    match_rate_pct: float

    def to_dict(self) -> Dict[str, Any]:
        """Convertit le DTO en dictionnaire."""
        return {
            "last_sync_supplier_invoices": (
                self.last_sync_supplier_invoices.to_dict()
                if self.last_sync_supplier_invoices
                else None
            ),
            "last_sync_customer_invoices": (
                self.last_sync_customer_invoices.to_dict()
                if self.last_sync_customer_invoices
                else None
            ),
            "last_sync_suppliers": (
                self.last_sync_suppliers.to_dict()
                if self.last_sync_suppliers
                else None
            ),
            "pending_count": self.pending_count,
            "matched_today_count": self.matched_today_count,
            "total_imported_invoices": self.total_imported_invoices,
            "total_matched_invoices": self.total_matched_invoices,
            "match_rate_pct": self.match_rate_pct,
        }
