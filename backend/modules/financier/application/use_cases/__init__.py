"""Use Cases du module Financier."""

from .fournisseur_use_cases import (
    CreateFournisseurUseCase,
    UpdateFournisseurUseCase,
    DeleteFournisseurUseCase,
    GetFournisseurUseCase,
    ListFournisseursUseCase,
    FournisseurNotFoundError,
    FournisseurSiretExistsError,
)
from .budget_use_cases import (
    CreateBudgetUseCase,
    UpdateBudgetUseCase,
    GetBudgetUseCase,
    GetBudgetByChantierUseCase,
    BudgetNotFoundError,
    BudgetAlreadyExistsError,
)
from .lot_budgetaire_use_cases import (
    CreateLotBudgetaireUseCase,
    UpdateLotBudgetaireUseCase,
    DeleteLotBudgetaireUseCase,
    GetLotBudgetaireUseCase,
    ListLotsBudgetairesUseCase,
    LotNotFoundError,
    LotCodeExistsError,
)
from .achat_use_cases import (
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
    AchatNotFoundError,
    FournisseurInactifError,
)
from .dashboard_use_cases import GetDashboardFinancierUseCase

__all__ = [
    # Fournisseur
    "CreateFournisseurUseCase",
    "UpdateFournisseurUseCase",
    "DeleteFournisseurUseCase",
    "GetFournisseurUseCase",
    "ListFournisseursUseCase",
    "FournisseurNotFoundError",
    "FournisseurSiretExistsError",
    # Budget
    "CreateBudgetUseCase",
    "UpdateBudgetUseCase",
    "GetBudgetUseCase",
    "GetBudgetByChantierUseCase",
    "BudgetNotFoundError",
    "BudgetAlreadyExistsError",
    # Lot Budgétaire
    "CreateLotBudgetaireUseCase",
    "UpdateLotBudgetaireUseCase",
    "DeleteLotBudgetaireUseCase",
    "GetLotBudgetaireUseCase",
    "ListLotsBudgetairesUseCase",
    "LotNotFoundError",
    "LotCodeExistsError",
    # Achat
    "CreateAchatUseCase",
    "UpdateAchatUseCase",
    "ValiderAchatUseCase",
    "RefuserAchatUseCase",
    "PasserCommandeAchatUseCase",
    "MarquerLivreAchatUseCase",
    "MarquerFactureAchatUseCase",
    "GetAchatUseCase",
    "ListAchatsUseCase",
    "ListAchatsEnAttenteUseCase",
    "AchatNotFoundError",
    "FournisseurInactifError",
    # Dashboard
    "GetDashboardFinancierUseCase",
]
