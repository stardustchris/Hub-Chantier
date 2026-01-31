"""Injection de dependances pour le module Financier."""

from fastapi import Depends
from sqlalchemy.orm import Session

from shared.infrastructure.database import get_db
from shared.infrastructure.event_bus import EventBus as CoreEventBus
from ...application.ports.event_bus import EventBus
from ..event_bus_impl import FinancierEventBus

from ...domain.repositories import (
    FournisseurRepository,
    BudgetRepository,
    LotBudgetaireRepository,
    AchatRepository,
    JournalFinancierRepository,
)
from ...application.use_cases import (
    # Fournisseur
    CreateFournisseurUseCase,
    UpdateFournisseurUseCase,
    DeleteFournisseurUseCase,
    GetFournisseurUseCase,
    ListFournisseursUseCase,
    # Budget
    CreateBudgetUseCase,
    UpdateBudgetUseCase,
    GetBudgetUseCase,
    GetBudgetByChantierUseCase,
    # Lot Budgetaire
    CreateLotBudgetaireUseCase,
    UpdateLotBudgetaireUseCase,
    DeleteLotBudgetaireUseCase,
    GetLotBudgetaireUseCase,
    ListLotsBudgetairesUseCase,
    # Achat
    CreateAchatUseCase,
    UpdateAchatUseCase,
    ValiderAchatUseCase,
    RefuserAchatUseCase,
    PasserCommandeAchatUseCase,
    MarquerLivreAchatUseCase,
    MarquerFactureAchatUseCase,
    GetAchatUseCase,
    ListAchatsUseCase,
    ListAchatsEnAttenteUseCase,
    # Dashboard
    GetDashboardFinancierUseCase,
)
from ..persistence import (
    SQLAlchemyFournisseurRepository,
    SQLAlchemyBudgetRepository,
    SQLAlchemyLotBudgetaireRepository,
    SQLAlchemyAchatRepository,
    SQLAlchemyJournalFinancierRepository,
)


# =============================================================================
# Infrastructure Dependencies
# =============================================================================


def get_event_bus() -> EventBus:
    """Retourne l'EventBus avec logging pour audit trail (H8)."""
    return FinancierEventBus(CoreEventBus)


def get_fournisseur_repository(
    db: Session = Depends(get_db),
) -> FournisseurRepository:
    """Retourne le repository Fournisseur."""
    return SQLAlchemyFournisseurRepository(db)


def get_budget_repository(
    db: Session = Depends(get_db),
) -> BudgetRepository:
    """Retourne le repository Budget."""
    return SQLAlchemyBudgetRepository(db)


def get_lot_budgetaire_repository(
    db: Session = Depends(get_db),
) -> LotBudgetaireRepository:
    """Retourne le repository LotBudgetaire."""
    return SQLAlchemyLotBudgetaireRepository(db)


def get_achat_repository(
    db: Session = Depends(get_db),
) -> AchatRepository:
    """Retourne le repository Achat."""
    return SQLAlchemyAchatRepository(db)


def get_journal_financier_repository(
    db: Session = Depends(get_db),
) -> JournalFinancierRepository:
    """Retourne le repository JournalFinancier."""
    return SQLAlchemyJournalFinancierRepository(db)


# =============================================================================
# Use Cases - Fournisseur (FIN-14)
# =============================================================================


def get_create_fournisseur_use_case(
    fournisseur_repository: FournisseurRepository = Depends(get_fournisseur_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> CreateFournisseurUseCase:
    """Retourne le use case CreateFournisseur."""
    return CreateFournisseurUseCase(fournisseur_repository, journal_repository, event_bus)


def get_update_fournisseur_use_case(
    fournisseur_repository: FournisseurRepository = Depends(get_fournisseur_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> UpdateFournisseurUseCase:
    """Retourne le use case UpdateFournisseur."""
    return UpdateFournisseurUseCase(fournisseur_repository, journal_repository, event_bus)


def get_delete_fournisseur_use_case(
    fournisseur_repository: FournisseurRepository = Depends(get_fournisseur_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> DeleteFournisseurUseCase:
    """Retourne le use case DeleteFournisseur."""
    return DeleteFournisseurUseCase(fournisseur_repository, journal_repository, event_bus)


def get_get_fournisseur_use_case(
    fournisseur_repository: FournisseurRepository = Depends(get_fournisseur_repository),
) -> GetFournisseurUseCase:
    """Retourne le use case GetFournisseur."""
    return GetFournisseurUseCase(fournisseur_repository)


def get_list_fournisseurs_use_case(
    fournisseur_repository: FournisseurRepository = Depends(get_fournisseur_repository),
) -> ListFournisseursUseCase:
    """Retourne le use case ListFournisseurs."""
    return ListFournisseursUseCase(fournisseur_repository)


# =============================================================================
# Use Cases - Budget (FIN-01)
# =============================================================================


def get_create_budget_use_case(
    budget_repository: BudgetRepository = Depends(get_budget_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> CreateBudgetUseCase:
    """Retourne le use case CreateBudget."""
    return CreateBudgetUseCase(budget_repository, journal_repository, event_bus)


def get_update_budget_use_case(
    budget_repository: BudgetRepository = Depends(get_budget_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> UpdateBudgetUseCase:
    """Retourne le use case UpdateBudget."""
    return UpdateBudgetUseCase(budget_repository, journal_repository, event_bus)


def get_get_budget_use_case(
    budget_repository: BudgetRepository = Depends(get_budget_repository),
) -> GetBudgetUseCase:
    """Retourne le use case GetBudget."""
    return GetBudgetUseCase(budget_repository)


def get_get_budget_by_chantier_use_case(
    budget_repository: BudgetRepository = Depends(get_budget_repository),
) -> GetBudgetByChantierUseCase:
    """Retourne le use case GetBudgetByChantier."""
    return GetBudgetByChantierUseCase(budget_repository)


# =============================================================================
# Use Cases - Lot Budgetaire (FIN-02)
# =============================================================================


def get_create_lot_budgetaire_use_case(
    lot_repository: LotBudgetaireRepository = Depends(get_lot_budgetaire_repository),
    budget_repository: BudgetRepository = Depends(get_budget_repository),
    achat_repository: AchatRepository = Depends(get_achat_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> CreateLotBudgetaireUseCase:
    """Retourne le use case CreateLotBudgetaire."""
    return CreateLotBudgetaireUseCase(
        lot_repository, budget_repository, achat_repository, journal_repository, event_bus
    )


def get_update_lot_budgetaire_use_case(
    lot_repository: LotBudgetaireRepository = Depends(get_lot_budgetaire_repository),
    achat_repository: AchatRepository = Depends(get_achat_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> UpdateLotBudgetaireUseCase:
    """Retourne le use case UpdateLotBudgetaire."""
    return UpdateLotBudgetaireUseCase(
        lot_repository, achat_repository, journal_repository, event_bus
    )


def get_delete_lot_budgetaire_use_case(
    lot_repository: LotBudgetaireRepository = Depends(get_lot_budgetaire_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> DeleteLotBudgetaireUseCase:
    """Retourne le use case DeleteLotBudgetaire."""
    return DeleteLotBudgetaireUseCase(lot_repository, journal_repository, event_bus)


def get_get_lot_budgetaire_use_case(
    lot_repository: LotBudgetaireRepository = Depends(get_lot_budgetaire_repository),
    achat_repository: AchatRepository = Depends(get_achat_repository),
) -> GetLotBudgetaireUseCase:
    """Retourne le use case GetLotBudgetaire."""
    return GetLotBudgetaireUseCase(lot_repository, achat_repository)


def get_list_lots_budgetaires_use_case(
    lot_repository: LotBudgetaireRepository = Depends(get_lot_budgetaire_repository),
    achat_repository: AchatRepository = Depends(get_achat_repository),
) -> ListLotsBudgetairesUseCase:
    """Retourne le use case ListLotsBudgetaires."""
    return ListLotsBudgetairesUseCase(lot_repository, achat_repository)


# =============================================================================
# Use Cases - Achat (FIN-05, FIN-06, FIN-07)
# =============================================================================


def get_create_achat_use_case(
    achat_repository: AchatRepository = Depends(get_achat_repository),
    fournisseur_repository: FournisseurRepository = Depends(get_fournisseur_repository),
    budget_repository: BudgetRepository = Depends(get_budget_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> CreateAchatUseCase:
    """Retourne le use case CreateAchat."""
    return CreateAchatUseCase(
        achat_repository, fournisseur_repository, budget_repository,
        journal_repository, event_bus,
    )


def get_update_achat_use_case(
    achat_repository: AchatRepository = Depends(get_achat_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> UpdateAchatUseCase:
    """Retourne le use case UpdateAchat."""
    return UpdateAchatUseCase(achat_repository, journal_repository, event_bus)


def get_valider_achat_use_case(
    achat_repository: AchatRepository = Depends(get_achat_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> ValiderAchatUseCase:
    """Retourne le use case ValiderAchat."""
    return ValiderAchatUseCase(achat_repository, journal_repository, event_bus)


def get_refuser_achat_use_case(
    achat_repository: AchatRepository = Depends(get_achat_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> RefuserAchatUseCase:
    """Retourne le use case RefuserAchat."""
    return RefuserAchatUseCase(achat_repository, journal_repository, event_bus)


def get_passer_commande_achat_use_case(
    achat_repository: AchatRepository = Depends(get_achat_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> PasserCommandeAchatUseCase:
    """Retourne le use case PasserCommandeAchat."""
    return PasserCommandeAchatUseCase(achat_repository, journal_repository, event_bus)


def get_marquer_livre_achat_use_case(
    achat_repository: AchatRepository = Depends(get_achat_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> MarquerLivreAchatUseCase:
    """Retourne le use case MarquerLivreAchat."""
    return MarquerLivreAchatUseCase(achat_repository, journal_repository, event_bus)


def get_marquer_facture_achat_use_case(
    achat_repository: AchatRepository = Depends(get_achat_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> MarquerFactureAchatUseCase:
    """Retourne le use case MarquerFactureAchat."""
    return MarquerFactureAchatUseCase(achat_repository, journal_repository, event_bus)


def get_get_achat_use_case(
    achat_repository: AchatRepository = Depends(get_achat_repository),
) -> GetAchatUseCase:
    """Retourne le use case GetAchat."""
    return GetAchatUseCase(achat_repository)


def get_list_achats_use_case(
    achat_repository: AchatRepository = Depends(get_achat_repository),
) -> ListAchatsUseCase:
    """Retourne le use case ListAchats."""
    return ListAchatsUseCase(achat_repository)


def get_list_achats_en_attente_use_case(
    achat_repository: AchatRepository = Depends(get_achat_repository),
) -> ListAchatsEnAttenteUseCase:
    """Retourne le use case ListAchatsEnAttente."""
    return ListAchatsEnAttenteUseCase(achat_repository)


# =============================================================================
# Use Cases - Dashboard (FIN-11)
# =============================================================================


def get_dashboard_financier_use_case(
    budget_repository: BudgetRepository = Depends(get_budget_repository),
    lot_repository: LotBudgetaireRepository = Depends(get_lot_budgetaire_repository),
    achat_repository: AchatRepository = Depends(get_achat_repository),
) -> GetDashboardFinancierUseCase:
    """Retourne le use case GetDashboardFinancier."""
    return GetDashboardFinancierUseCase(
        budget_repository, lot_repository, achat_repository
    )
