"""Dependencies FastAPI pour les routes Pennylane.

CONN-10 to CONN-17: Injection de dependances pour les use cases Pennylane.
"""

import os
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session

from shared.infrastructure.database import get_db
from shared.infrastructure.connectors.pennylane.api_client import PennylaneApiClient
from shared.infrastructure.connectors.pennylane.sync_service import PennylaneSyncService

from ...application.use_cases.pennylane_sync_use_cases import (
    SyncSupplierInvoicesUseCase,
    SyncCustomerInvoicesUseCase,
    SyncSuppliersUseCase,
    GetPendingReconciliationsUseCase,
    ResolveReconciliationUseCase,
    GetMappingsUseCase,
    CreateMappingUseCase,
    DeleteMappingUseCase,
    GetSyncHistoryUseCase,
)
from ..persistence.pennylane_repositories import (
    SqlAlchemyPennylaneSyncLogRepository,
    SqlAlchemyPennylaneMappingRepository,
    SqlAlchemyPennylanePendingRepository,
)
from ..persistence.repositories import (
    SqlAlchemyAchatRepository,
    SqlAlchemyFournisseurRepository,
    SqlAlchemyFactureClientRepository,
)
from modules.chantiers.infrastructure.persistence import SQLAlchemyChantierRepository


def get_pennylane_api_key() -> str:
    """Recupere la cle API Pennylane depuis les variables d'environnement."""
    api_key = os.environ.get("PENNYLANE_API_KEY", "")
    if not api_key:
        # En dev, on peut utiliser une cle de test
        api_key = os.environ.get("PENNYLANE_API_KEY_DEV", "dev_api_key_placeholder")
    return api_key


def get_pennylane_api_client() -> PennylaneApiClient:
    """Cree un client API Pennylane."""
    return PennylaneApiClient(
        api_key=get_pennylane_api_key(),
        timeout=30.0,
        max_retries=3,
    )


def get_sync_log_repository(
    db: Session = Depends(get_db),
) -> SqlAlchemyPennylaneSyncLogRepository:
    """Cree le repository des logs de sync."""
    return SqlAlchemyPennylaneSyncLogRepository(db)


def get_mapping_repository(
    db: Session = Depends(get_db),
) -> SqlAlchemyPennylaneMappingRepository:
    """Cree le repository des mappings analytiques."""
    return SqlAlchemyPennylaneMappingRepository(db)


def get_pending_repository(
    db: Session = Depends(get_db),
) -> SqlAlchemyPennylanePendingRepository:
    """Cree le repository des reconciliations en attente."""
    return SqlAlchemyPennylanePendingRepository(db)


def get_achat_repository(
    db: Session = Depends(get_db),
) -> SqlAlchemyAchatRepository:
    """Cree le repository des achats."""
    return SqlAlchemyAchatRepository(db)


def get_fournisseur_repository(
    db: Session = Depends(get_db),
) -> SqlAlchemyFournisseurRepository:
    """Cree le repository des fournisseurs."""
    return SqlAlchemyFournisseurRepository(db)


def get_facture_repository(
    db: Session = Depends(get_db),
) -> SqlAlchemyFactureClientRepository:
    """Cree le repository des factures client."""
    return SqlAlchemyFactureClientRepository(db)


def get_chantier_repository(
    db: Session = Depends(get_db),
) -> SQLAlchemyChantierRepository:
    """Cree le repository des chantiers."""
    return SQLAlchemyChantierRepository(db)


def get_pennylane_sync_service(
    achat_repo: SqlAlchemyAchatRepository = Depends(get_achat_repository),
    fournisseur_repo: SqlAlchemyFournisseurRepository = Depends(get_fournisseur_repository),
    facture_repo: SqlAlchemyFactureClientRepository = Depends(get_facture_repository),
    sync_log_repo: SqlAlchemyPennylaneSyncLogRepository = Depends(get_sync_log_repository),
    mapping_repo: SqlAlchemyPennylaneMappingRepository = Depends(get_mapping_repository),
    pending_repo: SqlAlchemyPennylanePendingRepository = Depends(get_pending_repository),
) -> PennylaneSyncService:
    """Cree le service de synchronisation Pennylane."""
    api_client = get_pennylane_api_client()
    return PennylaneSyncService(
        api_client=api_client,
        achat_repository=achat_repo,
        fournisseur_repository=fournisseur_repo,
        facture_repository=facture_repo,
        sync_log_repository=sync_log_repo,
        mapping_repository=mapping_repo,
        pending_repository=pending_repo,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Use Cases
# ─────────────────────────────────────────────────────────────────────────────

def get_sync_supplier_invoices_use_case(
    sync_service: PennylaneSyncService = Depends(get_pennylane_sync_service),
    sync_log_repo: SqlAlchemyPennylaneSyncLogRepository = Depends(get_sync_log_repository),
) -> SyncSupplierInvoicesUseCase:
    """Cree le use case de sync factures fournisseurs."""
    return SyncSupplierInvoicesUseCase(
        sync_service=sync_service,
        sync_log_repository=sync_log_repo,
    )


def get_sync_customer_invoices_use_case(
    sync_service: PennylaneSyncService = Depends(get_pennylane_sync_service),
    sync_log_repo: SqlAlchemyPennylaneSyncLogRepository = Depends(get_sync_log_repository),
) -> SyncCustomerInvoicesUseCase:
    """Cree le use case de sync encaissements clients."""
    return SyncCustomerInvoicesUseCase(
        sync_service=sync_service,
        sync_log_repository=sync_log_repo,
    )


def get_sync_suppliers_use_case(
    sync_service: PennylaneSyncService = Depends(get_pennylane_sync_service),
    sync_log_repo: SqlAlchemyPennylaneSyncLogRepository = Depends(get_sync_log_repository),
) -> SyncSuppliersUseCase:
    """Cree le use case de sync fournisseurs."""
    return SyncSuppliersUseCase(
        sync_service=sync_service,
        sync_log_repository=sync_log_repo,
    )


def get_pending_reconciliations_use_case(
    pending_repo: SqlAlchemyPennylanePendingRepository = Depends(get_pending_repository),
    achat_repo: SqlAlchemyAchatRepository = Depends(get_achat_repository),
) -> GetPendingReconciliationsUseCase:
    """Cree le use case de liste des reconciliations."""
    return GetPendingReconciliationsUseCase(
        pending_repository=pending_repo,
        achat_repository=achat_repo,
    )


def get_resolve_reconciliation_use_case(
    pending_repo: SqlAlchemyPennylanePendingRepository = Depends(get_pending_repository),
    achat_repo: SqlAlchemyAchatRepository = Depends(get_achat_repository),
) -> ResolveReconciliationUseCase:
    """Cree le use case de resolution de reconciliation."""
    return ResolveReconciliationUseCase(
        pending_repository=pending_repo,
        achat_repository=achat_repo,
    )


def get_mappings_use_case(
    mapping_repo: SqlAlchemyPennylaneMappingRepository = Depends(get_mapping_repository),
    chantier_repo: SQLAlchemyChantierRepository = Depends(get_chantier_repository),
) -> GetMappingsUseCase:
    """Cree le use case de liste des mappings."""
    return GetMappingsUseCase(
        mapping_repository=mapping_repo,
        chantier_repository=chantier_repo,
    )


def get_create_mapping_use_case(
    mapping_repo: SqlAlchemyPennylaneMappingRepository = Depends(get_mapping_repository),
    chantier_repo: SQLAlchemyChantierRepository = Depends(get_chantier_repository),
) -> CreateMappingUseCase:
    """Cree le use case de creation de mapping."""
    return CreateMappingUseCase(
        mapping_repository=mapping_repo,
        chantier_repository=chantier_repo,
    )


def get_delete_mapping_use_case(
    mapping_repo: SqlAlchemyPennylaneMappingRepository = Depends(get_mapping_repository),
) -> DeleteMappingUseCase:
    """Cree le use case de suppression de mapping."""
    return DeleteMappingUseCase(
        mapping_repository=mapping_repo,
    )


def get_sync_history_use_case(
    sync_log_repo: SqlAlchemyPennylaneSyncLogRepository = Depends(get_sync_log_repository),
) -> GetSyncHistoryUseCase:
    """Cree le use case d'historique des syncs."""
    return GetSyncHistoryUseCase(
        sync_log_repository=sync_log_repo,
    )
