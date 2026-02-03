"""Connecteur Pennylane pour comptabilite.

Outbound (export):
- PennylaneConnector: Export achats/situations/paiements vers Pennylane

Inbound (import - CONN-10 to CONN-17):
- PennylaneApiClient: Client HTTP pour l'API Pennylane v2
- PennylaneSyncService: Service de synchronisation periodique
"""

from .connector import PennylaneConnector
from .api_client import (
    PennylaneApiClient,
    PennylaneApiError,
    PennylaneRateLimitError,
    PennylaneAuthenticationError,
    PennylaneSupplierInvoice,
    PennylaneCustomerInvoice,
    PennylaneSupplier,
)
from .sync_service import (
    PennylaneSyncService,
    SyncResult,
    MatchResult,
)

__all__ = [
    # Outbound (export)
    "PennylaneConnector",
    # Inbound (import) - API Client
    "PennylaneApiClient",
    "PennylaneApiError",
    "PennylaneRateLimitError",
    "PennylaneAuthenticationError",
    "PennylaneSupplierInvoice",
    "PennylaneCustomerInvoice",
    "PennylaneSupplier",
    # Inbound (import) - Sync Service
    "PennylaneSyncService",
    "SyncResult",
    "MatchResult",
]
