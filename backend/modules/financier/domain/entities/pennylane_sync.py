"""Entites Pennylane Sync - Historique et reconciliation des synchronisations.

CONN-10: Sync factures fournisseurs Pennylane.
CONN-11: Sync encaissements clients Pennylane.
CONN-12: Import fournisseurs Pennylane.
CONN-14: Table mapping analytique.
CONN-15: Dashboard reconciliation.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Literal


# Types pour les statuts
SyncType = Literal["supplier_invoices", "customer_invoices", "suppliers"]
SyncStatus = Literal["running", "completed", "failed", "partial"]
ReconciliationStatus = Literal["pending", "matched", "rejected", "manual"]


@dataclass
class PennylaneSyncLog:
    """Entite representant un log de synchronisation Pennylane.

    CONN-10/11/12: Audit trail des synchronisations periodiques.
    Permet le suivi des imports et la detection des problemes.

    Attributes:
        id: Identifiant unique (None si non persiste).
        sync_type: Type de synchronisation (supplier_invoices, customer_invoices, suppliers).
        started_at: Date/heure de debut de la synchronisation.
        completed_at: Date/heure de fin (None si en cours).
        records_processed: Nombre total de records traites.
        records_created: Nombre de nouveaux records crees.
        records_updated: Nombre de records mis a jour.
        records_pending: Nombre de records en attente de reconciliation.
        error_message: Message d'erreur si echec.
        status: Statut de la synchronisation.
    """

    sync_type: SyncType
    started_at: datetime

    id: Optional[int] = None
    completed_at: Optional[datetime] = None
    records_processed: int = 0
    records_created: int = 0
    records_updated: int = 0
    records_pending: int = 0
    error_message: Optional[str] = None
    status: SyncStatus = "running"

    def __post_init__(self) -> None:
        """Validation a la creation."""
        if self.sync_type not in ("supplier_invoices", "customer_invoices", "suppliers"):
            raise ValueError(
                f"Type de sync invalide: {self.sync_type}. "
                "Valeurs autorisees: supplier_invoices, customer_invoices, suppliers"
            )

    def marquer_complete(
        self,
        records_processed: int = 0,
        records_created: int = 0,
        records_updated: int = 0,
        records_pending: int = 0,
    ) -> None:
        """Marque la synchronisation comme terminee avec succes.

        Args:
            records_processed: Nombre total de records traites.
            records_created: Nombre de nouveaux records.
            records_updated: Nombre de records mis a jour.
            records_pending: Nombre en attente de reconciliation.
        """
        self.completed_at = datetime.utcnow()
        self.records_processed = records_processed
        self.records_created = records_created
        self.records_updated = records_updated
        self.records_pending = records_pending
        self.status = "completed" if records_pending == 0 else "partial"

    def marquer_echec(self, error_message: str) -> None:
        """Marque la synchronisation comme echouee.

        Args:
            error_message: Message d'erreur descriptif.
        """
        self.completed_at = datetime.utcnow()
        self.error_message = error_message
        self.status = "failed"

    @property
    def duree_secondes(self) -> Optional[float]:
        """Calcule la duree de la synchronisation en secondes."""
        if self.completed_at is None:
            return None
        delta = self.completed_at - self.started_at
        return delta.total_seconds()

    @property
    def est_en_cours(self) -> bool:
        """Indique si la synchronisation est en cours."""
        return self.status == "running"

    @property
    def a_echoue(self) -> bool:
        """Indique si la synchronisation a echoue."""
        return self.status == "failed"

    def to_dict(self) -> dict:
        """Convertit l'entite en dictionnaire."""
        return {
            "id": self.id,
            "sync_type": self.sync_type,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "records_processed": self.records_processed,
            "records_created": self.records_created,
            "records_updated": self.records_updated,
            "records_pending": self.records_pending,
            "error_message": self.error_message,
            "status": self.status,
            "duree_secondes": self.duree_secondes,
        }


@dataclass
class PennylaneMappingAnalytique:
    """Entite representant un mapping code analytique Pennylane -> chantier.

    CONN-14: Table de correspondance entre les codes analytiques utilises
    dans Pennylane et les ID de chantiers dans Hub Chantier.

    Attributes:
        id: Identifiant unique (None si non persiste).
        code_analytique: Code analytique Pennylane (ex: MONTMELIAN, CHT001).
        chantier_id: ID du chantier Hub Chantier associe.
        created_at: Date de creation du mapping.
        created_by: ID de l'utilisateur ayant cree le mapping.
    """

    code_analytique: str
    chantier_id: int

    id: Optional[int] = None
    created_at: Optional[datetime] = None
    created_by: Optional[int] = None

    def __post_init__(self) -> None:
        """Validation a la creation."""
        if not self.code_analytique or not self.code_analytique.strip():
            raise ValueError("Le code analytique est obligatoire")
        if self.chantier_id <= 0:
            raise ValueError("L'ID du chantier doit etre positif")
        # Normaliser le code analytique (majuscules, sans espaces)
        self.code_analytique = self.code_analytique.strip().upper()

    def to_dict(self) -> dict:
        """Convertit l'entite en dictionnaire."""
        return {
            "id": self.id,
            "code_analytique": self.code_analytique,
            "chantier_id": self.chantier_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by,
        }


@dataclass
class PennylanePendingReconciliation:
    """Entite representant une facture Pennylane en attente de reconciliation.

    CONN-15: File d'attente des factures importees de Pennylane qui n'ont
    pas pu etre matchees automatiquement avec un achat existant.

    Attributes:
        id: Identifiant unique (None si non persiste).
        pennylane_invoice_id: ID unique de la facture Pennylane.
        supplier_name: Nom du fournisseur depuis Pennylane.
        supplier_siret: SIRET du fournisseur depuis Pennylane.
        amount_ht: Montant HT de la facture.
        code_analytique: Code analytique Pennylane associe.
        invoice_date: Date de la facture.
        suggested_achat_id: ID de l'achat suggere par le matching.
        status: Statut de la reconciliation.
        resolved_by: ID de l'utilisateur ayant resolu.
        resolved_at: Date/heure de resolution.
        created_at: Date de creation de la demande.
    """

    pennylane_invoice_id: str

    id: Optional[int] = None
    supplier_name: Optional[str] = None
    supplier_siret: Optional[str] = None
    amount_ht: Optional[Decimal] = None
    code_analytique: Optional[str] = None
    invoice_date: Optional[date] = None
    suggested_achat_id: Optional[int] = None
    status: ReconciliationStatus = "pending"
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validation a la creation."""
        if not self.pennylane_invoice_id or not self.pennylane_invoice_id.strip():
            raise ValueError("L'ID de facture Pennylane est obligatoire")

    def valider_match(self, resolved_by: int, achat_id: int) -> None:
        """Valide le match suggere ou choisi manuellement.

        Args:
            resolved_by: ID de l'utilisateur validant.
            achat_id: ID de l'achat matche.
        """
        if self.status != "pending":
            raise ValueError(
                f"Impossible de valider une reconciliation en statut '{self.status}'"
            )
        self.status = "matched"
        self.suggested_achat_id = achat_id
        self.resolved_by = resolved_by
        self.resolved_at = datetime.utcnow()

    def rejeter(self, resolved_by: int) -> None:
        """Rejette la facture (pas de match possible).

        Args:
            resolved_by: ID de l'utilisateur rejetant.
        """
        if self.status != "pending":
            raise ValueError(
                f"Impossible de rejeter une reconciliation en statut '{self.status}'"
            )
        self.status = "rejected"
        self.resolved_by = resolved_by
        self.resolved_at = datetime.utcnow()

    def creer_achat_manuel(self, resolved_by: int) -> None:
        """Marque pour creation manuelle d'un achat.

        Args:
            resolved_by: ID de l'utilisateur.
        """
        if self.status != "pending":
            raise ValueError(
                f"Impossible de marquer en manuel une reconciliation en statut '{self.status}'"
            )
        self.status = "manual"
        self.resolved_by = resolved_by
        self.resolved_at = datetime.utcnow()

    @property
    def est_resolue(self) -> bool:
        """Indique si la reconciliation est resolue."""
        return self.status != "pending"

    @property
    def ecart_match_pct(self) -> Optional[Decimal]:
        """Calcule l'ecart en pourcentage si un match est suggere.

        Note: Cette property necessite l'achat suggere pour calculer l'ecart.
        Elle retourne None car l'entite n'a pas acces au montant de l'achat.
        Le calcul reel est fait dans le service de matching.
        """
        return None

    def to_dict(self) -> dict:
        """Convertit l'entite en dictionnaire."""
        return {
            "id": self.id,
            "pennylane_invoice_id": self.pennylane_invoice_id,
            "supplier_name": self.supplier_name,
            "supplier_siret": self.supplier_siret,
            "amount_ht": str(self.amount_ht) if self.amount_ht else None,
            "code_analytique": self.code_analytique,
            "invoice_date": self.invoice_date.isoformat() if self.invoice_date else None,
            "suggested_achat_id": self.suggested_achat_id,
            "status": self.status,
            "resolved_by": self.resolved_by,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
