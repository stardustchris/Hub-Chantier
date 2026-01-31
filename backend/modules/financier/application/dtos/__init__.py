"""DTOs du module Financier."""

from .fournisseur_dtos import (
    FournisseurCreateDTO,
    FournisseurUpdateDTO,
    FournisseurDTO,
    FournisseurListDTO,
)
from .budget_dtos import (
    BudgetCreateDTO,
    BudgetUpdateDTO,
    BudgetDTO,
    BudgetSummaryDTO,
)
from .lot_budgetaire_dtos import (
    LotBudgetaireCreateDTO,
    LotBudgetaireUpdateDTO,
    LotBudgetaireDTO,
    LotBudgetaireListDTO,
)
from .achat_dtos import (
    AchatCreateDTO,
    AchatUpdateDTO,
    AchatDTO,
    AchatListDTO,
    AchatValidationDTO,
    AchatRefusDTO,
)
from .dashboard_dtos import (
    KPIFinancierDTO,
    DerniersAchatsDTO,
    DashboardFinancierDTO,
)

__all__ = [
    "FournisseurCreateDTO",
    "FournisseurUpdateDTO",
    "FournisseurDTO",
    "FournisseurListDTO",
    "BudgetCreateDTO",
    "BudgetUpdateDTO",
    "BudgetDTO",
    "BudgetSummaryDTO",
    "LotBudgetaireCreateDTO",
    "LotBudgetaireUpdateDTO",
    "LotBudgetaireDTO",
    "LotBudgetaireListDTO",
    "AchatCreateDTO",
    "AchatUpdateDTO",
    "AchatDTO",
    "AchatListDTO",
    "AchatValidationDTO",
    "AchatRefusDTO",
    "KPIFinancierDTO",
    "DerniersAchatsDTO",
    "DashboardFinancierDTO",
]
