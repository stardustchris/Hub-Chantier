"""Persistence layer - Financier module."""

from .models import (
    FournisseurModel,
    BudgetModel,
    LotBudgetaireModel,
    AchatModel,
    AvenantBudgetaireModel,
    SituationTravauxModel,
    LigneSituationModel,
    JournalFinancierModel,
    FactureClientModel,
    AlerteDepassementModel,
    AffectationBudgetTacheModel,
    FinancierBase,
)
from .sqlalchemy_fournisseur_repository import SQLAlchemyFournisseurRepository
from .sqlalchemy_budget_repository import SQLAlchemyBudgetRepository
from .sqlalchemy_lot_budgetaire_repository import SQLAlchemyLotBudgetaireRepository
from .sqlalchemy_achat_repository import SQLAlchemyAchatRepository
from .sqlalchemy_avenant_repository import SQLAlchemyAvenantRepository
from .sqlalchemy_situation_repository import (
    SQLAlchemySituationRepository,
    SQLAlchemyLigneSituationRepository,
)
from .sqlalchemy_journal_financier_repository import SQLAlchemyJournalFinancierRepository
from .sqlalchemy_facture_repository import SQLAlchemyFactureRepository
from .sqlalchemy_cout_main_oeuvre_repository import SQLAlchemyCoutMainOeuvreRepository
from .sqlalchemy_cout_materiel_repository import SQLAlchemyCoutMaterielRepository
from .sqlalchemy_alerte_repository import SQLAlchemyAlerteRepository
from .sqlalchemy_affectation_repository import SQLAlchemyAffectationBudgetTacheRepository

__all__ = [
    # Models
    "FournisseurModel",
    "BudgetModel",
    "LotBudgetaireModel",
    "AchatModel",
    "AvenantBudgetaireModel",
    "SituationTravauxModel",
    "LigneSituationModel",
    "JournalFinancierModel",
    "FactureClientModel",
    "AlerteDepassementModel",
    "AffectationBudgetTacheModel",
    "FinancierBase",
    # Repositories
    "SQLAlchemyFournisseurRepository",
    "SQLAlchemyBudgetRepository",
    "SQLAlchemyLotBudgetaireRepository",
    "SQLAlchemyAchatRepository",
    "SQLAlchemyAvenantRepository",
    "SQLAlchemySituationRepository",
    "SQLAlchemyLigneSituationRepository",
    "SQLAlchemyJournalFinancierRepository",
    "SQLAlchemyFactureRepository",
    "SQLAlchemyCoutMainOeuvreRepository",
    "SQLAlchemyCoutMaterielRepository",
    "SQLAlchemyAlerteRepository",
    "SQLAlchemyAffectationBudgetTacheRepository",
]
