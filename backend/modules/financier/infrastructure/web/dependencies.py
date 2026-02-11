"""Injection de dependances pour le module Financier."""

import logging
import os
from typing import Optional

from fastapi import Depends
from sqlalchemy.orm import Session

from shared.infrastructure.database import get_db
from shared.infrastructure.event_bus import EventBus as CoreEventBus
from ...application.ports.event_bus import EventBus
from ...application.ports.ai_suggestion_port import AISuggestionPort
from ..event_bus_impl import FinancierEventBus

logger = logging.getLogger(__name__)

from ...domain.repositories import (
    FournisseurRepository,
    BudgetRepository,
    LotBudgetaireRepository,
    AchatRepository,
    JournalFinancierRepository,
    AvenantRepository,
    SituationRepository,
    LigneSituationRepository,
    FactureRepository,
    CoutMainOeuvreRepository,
    CoutMaterielRepository,
    AlerteRepository,
    AffectationBudgetTacheRepository,
    ConfigurationEntrepriseRepository,
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
    # Avenant (FIN-04)
    CreateAvenantUseCase,
    UpdateAvenantUseCase,
    ValiderAvenantUseCase,
    GetAvenantUseCase,
    ListAvenantsUseCase,
    DeleteAvenantUseCase,
    # Situation (FIN-07)
    CreateSituationUseCase,
    UpdateSituationUseCase,
    SoumettreSituationUseCase,
    ValiderSituationUseCase,
    MarquerValideeClientUseCase,
    MarquerFactureeSituationUseCase,
    GetSituationUseCase,
    ListSituationsUseCase,
    DeleteSituationUseCase,
    # Facture (FIN-08)
    CreateFactureFromSituationUseCase,
    CreateFactureAcompteUseCase,
    EmettreFactureUseCase,
    EnvoyerFactureUseCase,
    MarquerPayeeFactureUseCase,
    AnnulerFactureUseCase,
    GetFactureUseCase,
    ListFacturesUseCase,
    # Couts (FIN-09, FIN-10)
    GetCoutMainOeuvreUseCase,
    GetCoutMaterielUseCase,
    # Alertes (FIN-12)
    VerifierDepassementUseCase,
    AcquitterAlerteUseCase,
    ListAlertesUseCase,
    # Dashboard
    GetDashboardFinancierUseCase,
    # Evolution financiere (FIN-17)
    GetEvolutionFinanciereUseCase,
    # Consolidation (FIN-20)
    GetVueConsolideeFinancesUseCase,
    # Suggestions (FIN-21/22)
    GetSuggestionsFinancieresUseCase,
    # Affectation (FIN-03)
    CreateAffectationBudgetTacheUseCase,
    DeleteAffectationBudgetTacheUseCase,
    ListAffectationsByChantierUseCase,
    GetAffectationsByTacheUseCase,
    # Export comptable (FIN-13)
    ExportComptableUseCase,
    # P&L (GAP #9)
    GetPnLChantierUseCase,
    # Bilan de cloture (GAP #10)
    GetBilanClotureUseCase,
    # Configuration entreprise
    GetConfigurationEntrepriseUseCase,
    UpdateConfigurationEntrepriseUseCase,
)
from ..persistence import (
    SQLAlchemyFournisseurRepository,
    SQLAlchemyBudgetRepository,
    SQLAlchemyLotBudgetaireRepository,
    SQLAlchemyAchatRepository,
    SQLAlchemyJournalFinancierRepository,
    SQLAlchemyAvenantRepository,
    SQLAlchemySituationRepository,
    SQLAlchemyLigneSituationRepository,
    SQLAlchemyFactureRepository,
    SQLAlchemyCoutMainOeuvreRepository,
    SQLAlchemyCoutMaterielRepository,
    SQLAlchemyAlerteRepository,
    SQLAlchemyAffectationBudgetTacheRepository,
    SQLAlchemyConfigurationEntrepriseRepository,
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
    fournisseur_repository: FournisseurRepository = Depends(get_fournisseur_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> UpdateAchatUseCase:
    """Retourne le use case UpdateAchat."""
    return UpdateAchatUseCase(
        achat_repository, fournisseur_repository, journal_repository, event_bus,
    )


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
# Use Cases - Evolution Financiere (FIN-17)
# =============================================================================


def get_evolution_financiere_use_case(
    budget_repository: BudgetRepository = Depends(get_budget_repository),
    achat_repository: AchatRepository = Depends(get_achat_repository),
) -> GetEvolutionFinanciereUseCase:
    """Retourne le use case GetEvolutionFinanciere."""
    return GetEvolutionFinanciereUseCase(
        budget_repository, achat_repository
    )


# =============================================================================
# Repositories - Avenant (FIN-04)
# =============================================================================


def get_avenant_repository(
    db: Session = Depends(get_db),
) -> AvenantRepository:
    """Retourne le repository Avenant."""
    return SQLAlchemyAvenantRepository(db)


# =============================================================================
# Use Cases - Avenant (FIN-04)
# =============================================================================


def get_create_avenant_use_case(
    avenant_repository: AvenantRepository = Depends(get_avenant_repository),
    budget_repository: BudgetRepository = Depends(get_budget_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> CreateAvenantUseCase:
    """Retourne le use case CreateAvenant."""
    return CreateAvenantUseCase(
        avenant_repository, budget_repository, journal_repository, event_bus
    )


def get_update_avenant_use_case(
    avenant_repository: AvenantRepository = Depends(get_avenant_repository),
    budget_repository: BudgetRepository = Depends(get_budget_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
) -> UpdateAvenantUseCase:
    """Retourne le use case UpdateAvenant."""
    return UpdateAvenantUseCase(
        avenant_repository, budget_repository, journal_repository
    )


def get_valider_avenant_use_case(
    avenant_repository: AvenantRepository = Depends(get_avenant_repository),
    budget_repository: BudgetRepository = Depends(get_budget_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> ValiderAvenantUseCase:
    """Retourne le use case ValiderAvenant."""
    return ValiderAvenantUseCase(
        avenant_repository, budget_repository, journal_repository, event_bus
    )


def get_get_avenant_use_case(
    avenant_repository: AvenantRepository = Depends(get_avenant_repository),
) -> GetAvenantUseCase:
    """Retourne le use case GetAvenant."""
    return GetAvenantUseCase(avenant_repository)


def get_list_avenants_use_case(
    avenant_repository: AvenantRepository = Depends(get_avenant_repository),
) -> ListAvenantsUseCase:
    """Retourne le use case ListAvenants."""
    return ListAvenantsUseCase(avenant_repository)


def get_delete_avenant_use_case(
    avenant_repository: AvenantRepository = Depends(get_avenant_repository),
    budget_repository: BudgetRepository = Depends(get_budget_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
) -> DeleteAvenantUseCase:
    """Retourne le use case DeleteAvenant."""
    return DeleteAvenantUseCase(
        avenant_repository, budget_repository, journal_repository
    )


# =============================================================================
# Repositories - Situation (FIN-07)
# =============================================================================


def get_situation_repository(
    db: Session = Depends(get_db),
) -> SituationRepository:
    """Retourne le repository Situation."""
    return SQLAlchemySituationRepository(db)


def get_ligne_situation_repository(
    db: Session = Depends(get_db),
) -> LigneSituationRepository:
    """Retourne le repository LigneSituation."""
    return SQLAlchemyLigneSituationRepository(db)


# =============================================================================
# Use Cases - Situation (FIN-07)
# =============================================================================


def get_create_situation_use_case(
    situation_repository: SituationRepository = Depends(get_situation_repository),
    ligne_repository: LigneSituationRepository = Depends(get_ligne_situation_repository),
    budget_repository: BudgetRepository = Depends(get_budget_repository),
    lot_repository: LotBudgetaireRepository = Depends(get_lot_budgetaire_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> CreateSituationUseCase:
    """Retourne le use case CreateSituation."""
    return CreateSituationUseCase(
        situation_repository, ligne_repository, budget_repository,
        lot_repository, journal_repository, event_bus,
    )


def get_update_situation_use_case(
    situation_repository: SituationRepository = Depends(get_situation_repository),
    ligne_repository: LigneSituationRepository = Depends(get_ligne_situation_repository),
    lot_repository: LotBudgetaireRepository = Depends(get_lot_budgetaire_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
) -> UpdateSituationUseCase:
    """Retourne le use case UpdateSituation."""
    return UpdateSituationUseCase(
        situation_repository, ligne_repository, lot_repository, journal_repository
    )


def get_soumettre_situation_use_case(
    situation_repository: SituationRepository = Depends(get_situation_repository),
    ligne_repository: LigneSituationRepository = Depends(get_ligne_situation_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
) -> SoumettreSituationUseCase:
    """Retourne le use case SoumettreSituation."""
    return SoumettreSituationUseCase(
        situation_repository, ligne_repository, journal_repository
    )


def get_valider_situation_use_case(
    situation_repository: SituationRepository = Depends(get_situation_repository),
    ligne_repository: LigneSituationRepository = Depends(get_ligne_situation_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> ValiderSituationUseCase:
    """Retourne le use case ValiderSituation."""
    return ValiderSituationUseCase(
        situation_repository, ligne_repository, journal_repository, event_bus
    )


def get_marquer_validee_client_use_case(
    situation_repository: SituationRepository = Depends(get_situation_repository),
    ligne_repository: LigneSituationRepository = Depends(get_ligne_situation_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> MarquerValideeClientUseCase:
    """Retourne le use case MarquerValideeClient."""
    return MarquerValideeClientUseCase(
        situation_repository, ligne_repository, journal_repository, event_bus
    )


def get_marquer_facturee_situation_use_case(
    situation_repository: SituationRepository = Depends(get_situation_repository),
    ligne_repository: LigneSituationRepository = Depends(get_ligne_situation_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> MarquerFactureeSituationUseCase:
    """Retourne le use case MarquerFactureeSituation."""
    return MarquerFactureeSituationUseCase(
        situation_repository, ligne_repository, journal_repository, event_bus
    )


def get_get_situation_use_case(
    situation_repository: SituationRepository = Depends(get_situation_repository),
    ligne_repository: LigneSituationRepository = Depends(get_ligne_situation_repository),
) -> GetSituationUseCase:
    """Retourne le use case GetSituation."""
    return GetSituationUseCase(situation_repository, ligne_repository)


def get_list_situations_use_case(
    situation_repository: SituationRepository = Depends(get_situation_repository),
    ligne_repository: LigneSituationRepository = Depends(get_ligne_situation_repository),
) -> ListSituationsUseCase:
    """Retourne le use case ListSituations."""
    return ListSituationsUseCase(situation_repository, ligne_repository)


def get_delete_situation_use_case(
    situation_repository: SituationRepository = Depends(get_situation_repository),
    ligne_repository: LigneSituationRepository = Depends(get_ligne_situation_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
) -> DeleteSituationUseCase:
    """Retourne le use case DeleteSituation."""
    return DeleteSituationUseCase(
        situation_repository, ligne_repository, journal_repository
    )


# =============================================================================
# Repositories - Facture (FIN-08)
# =============================================================================


def get_facture_repository(
    db: Session = Depends(get_db),
) -> FactureRepository:
    """Retourne le repository Facture."""
    return SQLAlchemyFactureRepository(db)


# =============================================================================
# Use Cases - Facture (FIN-08)
# =============================================================================


def get_create_facture_from_situation_use_case(
    facture_repository: FactureRepository = Depends(get_facture_repository),
    situation_repository: SituationRepository = Depends(get_situation_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> CreateFactureFromSituationUseCase:
    """Retourne le use case CreateFactureFromSituation."""
    return CreateFactureFromSituationUseCase(
        facture_repository, situation_repository, journal_repository, event_bus
    )


def get_create_facture_acompte_use_case(
    facture_repository: FactureRepository = Depends(get_facture_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> CreateFactureAcompteUseCase:
    """Retourne le use case CreateFactureAcompte."""
    return CreateFactureAcompteUseCase(
        facture_repository, journal_repository, event_bus
    )


def get_emettre_facture_use_case(
    facture_repository: FactureRepository = Depends(get_facture_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> EmettreFactureUseCase:
    """Retourne le use case EmettreFacture."""
    return EmettreFactureUseCase(
        facture_repository, journal_repository, event_bus
    )


def get_envoyer_facture_use_case(
    facture_repository: FactureRepository = Depends(get_facture_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
) -> EnvoyerFactureUseCase:
    """Retourne le use case EnvoyerFacture."""
    return EnvoyerFactureUseCase(facture_repository, journal_repository)


def get_marquer_payee_facture_use_case(
    facture_repository: FactureRepository = Depends(get_facture_repository),
    situation_repository: SituationRepository = Depends(get_situation_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> MarquerPayeeFactureUseCase:
    """Retourne le use case MarquerPayeeFacture."""
    return MarquerPayeeFactureUseCase(
        facture_repository, situation_repository, journal_repository, event_bus
    )


def get_annuler_facture_use_case(
    facture_repository: FactureRepository = Depends(get_facture_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
) -> AnnulerFactureUseCase:
    """Retourne le use case AnnulerFacture."""
    return AnnulerFactureUseCase(facture_repository, journal_repository)


def get_get_facture_use_case(
    facture_repository: FactureRepository = Depends(get_facture_repository),
) -> GetFactureUseCase:
    """Retourne le use case GetFacture."""
    return GetFactureUseCase(facture_repository)


def get_list_factures_use_case(
    facture_repository: FactureRepository = Depends(get_facture_repository),
) -> ListFacturesUseCase:
    """Retourne le use case ListFactures."""
    return ListFacturesUseCase(facture_repository)


# =============================================================================
# Repositories - Couts Main-d'Oeuvre (FIN-09)
# =============================================================================


def get_cout_main_oeuvre_repository(
    db: Session = Depends(get_db),
) -> CoutMainOeuvreRepository:
    """Retourne le repository CoutMainOeuvre."""
    return SQLAlchemyCoutMainOeuvreRepository(db)


# =============================================================================
# Use Cases - Couts Main-d'Oeuvre (FIN-09)
# =============================================================================


def get_cout_main_oeuvre_use_case(
    cout_mo_repository: CoutMainOeuvreRepository = Depends(get_cout_main_oeuvre_repository),
) -> GetCoutMainOeuvreUseCase:
    """Retourne le use case GetCoutMainOeuvre."""
    return GetCoutMainOeuvreUseCase(cout_mo_repository)


# =============================================================================
# Repositories - Couts Materiel (FIN-10)
# =============================================================================


def get_cout_materiel_repository(
    db: Session = Depends(get_db),
) -> CoutMaterielRepository:
    """Retourne le repository CoutMateriel."""
    return SQLAlchemyCoutMaterielRepository(db)


# =============================================================================
# Use Cases - Couts Materiel (FIN-10)
# =============================================================================


def get_cout_materiel_use_case(
    cout_materiel_repository: CoutMaterielRepository = Depends(get_cout_materiel_repository),
) -> GetCoutMaterielUseCase:
    """Retourne le use case GetCoutMateriel."""
    return GetCoutMaterielUseCase(cout_materiel_repository)


# =============================================================================
# Use Cases - Dashboard (FIN-11)
# Note: Placé après les repositories CoutMainOeuvreRepository et CoutMaterielRepository
# =============================================================================


def get_dashboard_financier_use_case(
    budget_repository: BudgetRepository = Depends(get_budget_repository),
    lot_repository: LotBudgetaireRepository = Depends(get_lot_budgetaire_repository),
    achat_repository: AchatRepository = Depends(get_achat_repository),
    situation_repository: SituationRepository = Depends(get_situation_repository),
    cout_mo_repository: CoutMainOeuvreRepository = Depends(get_cout_main_oeuvre_repository),
    cout_materiel_repository: CoutMaterielRepository = Depends(get_cout_materiel_repository),
    facture_repository: FactureRepository = Depends(get_facture_repository),
) -> GetDashboardFinancierUseCase:
    """Retourne le use case GetDashboardFinancier.

    Utilise la formule BTP correcte pour le calcul de marge:
    Marge = (Prix Vente - Cout Revient) / Prix Vente
    ou Prix Vente = situations facturees, Cout Revient = achats + MO + materiel.
    Le facture_repository permet l'auto-calcul du CA total annuel (P1-1).
    """
    return GetDashboardFinancierUseCase(
        budget_repository, lot_repository, achat_repository,
        situation_repository, cout_mo_repository, cout_materiel_repository,
        facture_repository=facture_repository,
    )


# =============================================================================
# Repositories - Alertes (FIN-12)
# =============================================================================


def get_alerte_repository(
    db: Session = Depends(get_db),
) -> AlerteRepository:
    """Retourne le repository Alerte."""
    return SQLAlchemyAlerteRepository(db)


# =============================================================================
# Use Cases - Alertes (FIN-12)
# =============================================================================


def get_verifier_depassement_use_case(
    alerte_repository: AlerteRepository = Depends(get_alerte_repository),
    budget_repository: BudgetRepository = Depends(get_budget_repository),
    achat_repository: AchatRepository = Depends(get_achat_repository),
    cout_mo_repository: CoutMainOeuvreRepository = Depends(get_cout_main_oeuvre_repository),
    cout_materiel_repository: CoutMaterielRepository = Depends(get_cout_materiel_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> VerifierDepassementUseCase:
    """Retourne le use case VerifierDepassement."""
    return VerifierDepassementUseCase(
        alerte_repository, budget_repository, achat_repository,
        cout_mo_repository, cout_materiel_repository,
        journal_repository, event_bus,
    )


def get_acquitter_alerte_use_case(
    alerte_repository: AlerteRepository = Depends(get_alerte_repository),
    journal_repository: JournalFinancierRepository = Depends(get_journal_financier_repository),
) -> AcquitterAlerteUseCase:
    """Retourne le use case AcquitterAlerte."""
    return AcquitterAlerteUseCase(alerte_repository, journal_repository)


def get_list_alertes_use_case(
    alerte_repository: AlerteRepository = Depends(get_alerte_repository),
) -> ListAlertesUseCase:
    """Retourne le use case ListAlertes."""
    return ListAlertesUseCase(alerte_repository)


# =============================================================================
# Use Cases - Consolidation (FIN-20)
# =============================================================================


def get_vue_consolidee_use_case(
    budget_repository: BudgetRepository = Depends(get_budget_repository),
    lot_repository: LotBudgetaireRepository = Depends(get_lot_budgetaire_repository),
    achat_repository: AchatRepository = Depends(get_achat_repository),
    alerte_repository: AlerteRepository = Depends(get_alerte_repository),
    situation_repository: SituationRepository = Depends(get_situation_repository),
    cout_mo_repository: CoutMainOeuvreRepository = Depends(get_cout_main_oeuvre_repository),
    cout_materiel_repository: CoutMaterielRepository = Depends(get_cout_materiel_repository),
    db: Session = Depends(get_db),
) -> GetVueConsolideeFinancesUseCase:
    """Retourne le use case GetVueConsolideeFinances.

    Utilise la formule BTP correcte pour le calcul de marge:
    Marge = (CA HT - Cout Revient) / CA HT
    ou CA HT = situations facturees, Cout Revient = achats + MO + materiel + FG.
    La marge moyenne est ponderee par le prix de vente.
    """
    from modules.chantiers.infrastructure.persistence.sqlalchemy_chantier_repository import (
        SQLAlchemyChantierRepository,
    )
    from shared.infrastructure.adapters.chantier_info_adapter import ChantierInfoAdapter

    chantier_repo = SQLAlchemyChantierRepository(db)
    chantier_info_port = ChantierInfoAdapter(chantier_repo)

    return GetVueConsolideeFinancesUseCase(
        budget_repository, lot_repository, achat_repository, alerte_repository,
        chantier_info_port=chantier_info_port,
        situation_repository=situation_repository,
        cout_mo_repository=cout_mo_repository,
        cout_materiel_repository=cout_materiel_repository,
    )


# =============================================================================
# AI Provider - Suggestions IA (FIN-21)
# =============================================================================


# Singleton pour eviter de re-initialiser le provider a chaque requete
_ai_provider_instance: Optional[AISuggestionPort] = None
_ai_provider_initialized: bool = False


def get_ai_suggestion_provider() -> Optional[AISuggestionPort]:
    """Retourne le provider IA Gemini si GEMINI_API_KEY est configuree.

    Utilise un singleton pour eviter de re-initialiser le client Gemini
    a chaque requete. Si la cle n'est pas configuree ou si l'initialisation
    echoue, retourne None (fallback aux regles algorithmiques).

    Returns:
        GeminiSuggestionProvider si configure, None sinon.
    """
    global _ai_provider_instance, _ai_provider_initialized

    if _ai_provider_initialized:
        return _ai_provider_instance

    _ai_provider_initialized = True

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        logger.info(
            "GEMINI_API_KEY non configuree. "
            "Suggestions IA desactivees (mode algorithmique uniquement)."
        )
        return None

    try:
        from ..ai.gemini_provider import GeminiSuggestionProvider

        _ai_provider_instance = GeminiSuggestionProvider()
        logger.info("Provider IA Gemini initialise avec succes.")
        return _ai_provider_instance
    except Exception as e:
        logger.warning(
            "Impossible d'initialiser le provider Gemini: %s. "
            "Fallback aux regles algorithmiques.",
            str(e),
        )
        return None


# =============================================================================
# Use Cases - Suggestions (FIN-21/22)
# =============================================================================


def get_suggestions_financieres_use_case(
    budget_repository: BudgetRepository = Depends(get_budget_repository),
    achat_repository: AchatRepository = Depends(get_achat_repository),
    lot_repository: LotBudgetaireRepository = Depends(get_lot_budgetaire_repository),
    alerte_repository: AlerteRepository = Depends(get_alerte_repository),
    cout_mo_repository: CoutMainOeuvreRepository = Depends(get_cout_main_oeuvre_repository),
    cout_materiel_repository: CoutMaterielRepository = Depends(get_cout_materiel_repository),
) -> GetSuggestionsFinancieresUseCase:
    """Retourne le use case GetSuggestionsFinancieres avec provider IA optionnel."""
    ai_provider = get_ai_suggestion_provider()
    return GetSuggestionsFinancieresUseCase(
        budget_repository, achat_repository, lot_repository, alerte_repository,
        ai_provider=ai_provider,
        cout_mo_repository=cout_mo_repository,
        cout_materiel_repository=cout_materiel_repository,
    )


# =============================================================================
# Repositories - Affectation Budget-Tache (FIN-03)
# =============================================================================


def get_affectation_repository(
    db: Session = Depends(get_db),
) -> AffectationBudgetTacheRepository:
    """Retourne le repository AffectationBudgetTache."""
    return SQLAlchemyAffectationBudgetTacheRepository(db)


# =============================================================================
# Use Cases - Affectation Budget-Tache (FIN-03)
# =============================================================================


def get_create_affectation_use_case(
    affectation_repository: AffectationBudgetTacheRepository = Depends(get_affectation_repository),
    lot_repository: LotBudgetaireRepository = Depends(get_lot_budgetaire_repository),
) -> CreateAffectationBudgetTacheUseCase:
    """Retourne le use case CreateAffectationBudgetTache."""
    return CreateAffectationBudgetTacheUseCase(affectation_repository, lot_repository)


def get_delete_affectation_use_case(
    affectation_repository: AffectationBudgetTacheRepository = Depends(get_affectation_repository),
) -> DeleteAffectationBudgetTacheUseCase:
    """Retourne le use case DeleteAffectationBudgetTache."""
    return DeleteAffectationBudgetTacheUseCase(affectation_repository)


def get_list_affectations_by_chantier_use_case(
    affectation_repository: AffectationBudgetTacheRepository = Depends(get_affectation_repository),
    lot_repository: LotBudgetaireRepository = Depends(get_lot_budgetaire_repository),
) -> ListAffectationsByChantierUseCase:
    """Retourne le use case ListAffectationsByChantier."""
    return ListAffectationsByChantierUseCase(affectation_repository, lot_repository)


def get_affectations_by_tache_use_case(
    affectation_repository: AffectationBudgetTacheRepository = Depends(get_affectation_repository),
    lot_repository: LotBudgetaireRepository = Depends(get_lot_budgetaire_repository),
) -> GetAffectationsByTacheUseCase:
    """Retourne le use case GetAffectationsByTache."""
    return GetAffectationsByTacheUseCase(affectation_repository, lot_repository)


# =============================================================================
# Use Cases - Export Comptable (FIN-13)
# =============================================================================


def get_export_comptable_use_case(
    budget_repository: BudgetRepository = Depends(get_budget_repository),
    achat_repository: AchatRepository = Depends(get_achat_repository),
    situation_repository: SituationRepository = Depends(get_situation_repository),
    facture_repository: FactureRepository = Depends(get_facture_repository),
    fournisseur_repository: FournisseurRepository = Depends(get_fournisseur_repository),
    lot_repository: LotBudgetaireRepository = Depends(get_lot_budgetaire_repository),
) -> ExportComptableUseCase:
    """Retourne le use case ExportComptable."""
    return ExportComptableUseCase(
        budget_repository, achat_repository, situation_repository,
        facture_repository, fournisseur_repository, lot_repository,
    )


# =============================================================================
# Use Cases - P&L (GAP #9)
# =============================================================================


def get_pnl_chantier_use_case(
    facture_repository: FactureRepository = Depends(get_facture_repository),
    achat_repository: AchatRepository = Depends(get_achat_repository),
    budget_repository: BudgetRepository = Depends(get_budget_repository),
    cout_mo_repository: CoutMainOeuvreRepository = Depends(get_cout_main_oeuvre_repository),
    cout_materiel_repository: CoutMaterielRepository = Depends(get_cout_materiel_repository),
    db: Session = Depends(get_db),
) -> GetPnLChantierUseCase:
    """Retourne le use case GetPnLChantier."""
    from modules.chantiers.infrastructure.persistence.sqlalchemy_chantier_repository import (
        SQLAlchemyChantierRepository,
    )
    from shared.infrastructure.adapters.chantier_info_adapter import ChantierInfoAdapter

    chantier_repo = SQLAlchemyChantierRepository(db)
    chantier_info_port = ChantierInfoAdapter(chantier_repo)

    return GetPnLChantierUseCase(
        facture_repository, achat_repository, budget_repository,
        cout_mo_repository, cout_materiel_repository,
        chantier_info_port=chantier_info_port,
    )


# =============================================================================
# Use Cases - Bilan de Cloture (GAP #10)
# =============================================================================


def get_bilan_cloture_use_case(
    budget_repository: BudgetRepository = Depends(get_budget_repository),
    lot_repository: LotBudgetaireRepository = Depends(get_lot_budgetaire_repository),
    achat_repository: AchatRepository = Depends(get_achat_repository),
    avenant_repository: AvenantRepository = Depends(get_avenant_repository),
    situation_repository: SituationRepository = Depends(get_situation_repository),
    facture_repository: FactureRepository = Depends(get_facture_repository),
    cout_mo_repository: CoutMainOeuvreRepository = Depends(get_cout_main_oeuvre_repository),
    cout_materiel_repository: CoutMaterielRepository = Depends(get_cout_materiel_repository),
    db: Session = Depends(get_db),
) -> GetBilanClotureUseCase:
    """Retourne le use case GetBilanCloture."""
    from modules.chantiers.infrastructure.persistence.sqlalchemy_chantier_repository import (
        SQLAlchemyChantierRepository,
    )
    from shared.infrastructure.adapters.chantier_info_adapter import ChantierInfoAdapter

    chantier_repo = SQLAlchemyChantierRepository(db)
    chantier_info_port = ChantierInfoAdapter(chantier_repo)

    return GetBilanClotureUseCase(
        budget_repository, lot_repository, achat_repository,
        avenant_repository, situation_repository,
        chantier_info_port=chantier_info_port,
        facture_repository=facture_repository,
        cout_mo_repository=cout_mo_repository,
        cout_materiel_repository=cout_materiel_repository,
    )


# =============================================================================
# Repositories - Configuration Entreprise
# =============================================================================


def get_configuration_entreprise_repository(
    db: Session = Depends(get_db),
) -> ConfigurationEntrepriseRepository:
    """Retourne le repository ConfigurationEntreprise."""
    return SQLAlchemyConfigurationEntrepriseRepository(db)


# =============================================================================
# Use Cases - Configuration Entreprise
# =============================================================================


def get_get_configuration_entreprise_use_case(
    config_repository: ConfigurationEntrepriseRepository = Depends(
        get_configuration_entreprise_repository
    ),
) -> GetConfigurationEntrepriseUseCase:
    """Retourne le use case GetConfigurationEntreprise."""
    return GetConfigurationEntrepriseUseCase(config_repository)


def get_update_configuration_entreprise_use_case(
    config_repository: ConfigurationEntrepriseRepository = Depends(
        get_configuration_entreprise_repository
    ),
) -> UpdateConfigurationEntrepriseUseCase:
    """Retourne le use case UpdateConfigurationEntreprise."""
    return UpdateConfigurationEntrepriseUseCase(config_repository)
