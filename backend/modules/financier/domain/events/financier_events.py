"""Domain Events du module Financier.

Ces events permettent de découpler les actions et déclencher
des side effects (notifications, logs, alertes budget, etc.).
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional
import uuid


# --- Fournisseur Events ---


@dataclass(frozen=True)
class FournisseurCreatedEvent:
    """Event émis lors de la création d'un fournisseur.

    FIN-14: Répertoire fournisseurs.
    """

    fournisseur_id: int
    raison_sociale: str
    type_fournisseur: str
    created_by: int
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class FournisseurUpdatedEvent:
    """Event émis lors de la modification d'un fournisseur."""

    fournisseur_id: int
    raison_sociale: str
    updated_by: int
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class FournisseurDeletedEvent:
    """Event émis lors de la suppression d'un fournisseur."""

    fournisseur_id: int
    deleted_by: int
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)


# --- Budget Events ---


@dataclass(frozen=True)
class BudgetCreatedEvent:
    """Event émis lors de la création d'un budget.

    FIN-01: Budget prévisionnel.
    """

    budget_id: int
    chantier_id: int
    montant_initial_ht: Decimal
    created_by: int
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class BudgetUpdatedEvent:
    """Event émis lors de la modification d'un budget."""

    budget_id: int
    chantier_id: int
    montant_revise_ht: Decimal
    updated_by: int
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)


# --- Lot Budgétaire Events ---


@dataclass(frozen=True)
class LotBudgetaireCreatedEvent:
    """Event émis lors de la création d'un lot budgétaire.

    FIN-02: Décomposition en lots.
    """

    lot_id: int
    budget_id: int
    code_lot: str
    libelle: str
    total_prevu_ht: Decimal
    created_by: int
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class LotBudgetaireUpdatedEvent:
    """Event émis lors de la modification d'un lot budgétaire."""

    lot_id: int
    budget_id: int
    code_lot: str
    total_prevu_ht: Decimal
    updated_by: int
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class LotBudgetaireDeletedEvent:
    """Event émis lors de la suppression d'un lot budgétaire."""

    lot_id: int
    budget_id: int
    deleted_by: int
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)


# --- Achat Events ---


@dataclass(frozen=True)
class AchatCreatedEvent:
    """Event émis lors de la création d'un achat.

    FIN-05: Saisie achat.
    """

    achat_id: int
    chantier_id: int
    fournisseur_id: Optional[int]
    type_achat: str
    libelle: str
    total_ht: Decimal
    demandeur_id: Optional[int]
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class AchatValideEvent:
    """Event émis lors de la validation d'un achat.

    FIN-06: Suivi achat - Workflow validation.
    """

    achat_id: int
    chantier_id: int
    total_ht: Decimal
    valideur_id: int
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class AchatRefuseEvent:
    """Event émis lors du refus d'un achat."""

    achat_id: int
    chantier_id: int
    valideur_id: int
    motif: str
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class AchatCommandeEvent:
    """Event émis lors du passage en commande d'un achat."""

    achat_id: int
    chantier_id: int
    fournisseur_id: Optional[int]
    total_ht: Decimal
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class AchatLivreEvent:
    """Event émis lors de la réception d'un achat."""

    achat_id: int
    chantier_id: int
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class AchatFactureEvent:
    """Event émis lors de la facturation d'un achat."""

    achat_id: int
    chantier_id: int
    numero_facture: str
    total_ttc: Decimal
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)


# --- Alertes Budget ---


@dataclass(frozen=True)
class DepassementBudgetEvent:
    """Event émis lors d'un dépassement de seuil budgétaire.

    FIN-12: Alertes dépassement budget.
    """

    chantier_id: int
    budget_id: int
    montant_budget_ht: Decimal
    montant_engage_ht: Decimal
    pourcentage_consomme: Decimal
    seuil_alerte_pct: Decimal
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)


# --- Journal Events ---


@dataclass(frozen=True)
class JournalEntryCreatedEvent:
    """Event émis lors de la création d'une entrée dans le journal."""

    journal_entry_id: int
    entite_type: str
    entite_id: int
    action: str
    auteur_id: int
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)
