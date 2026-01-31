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
from .avenant_dtos import (
    AvenantCreateDTO,
    AvenantUpdateDTO,
    AvenantDTO,
)
from .situation_dtos import (
    SituationCreateDTO,
    SituationUpdateDTO,
    SituationDTO,
    LigneSituationCreateDTO,
    LigneSituationDTO,
)
from .facture_dtos import (
    FactureCreateDTO,
    FactureUpdateDTO,
    FactureDTO,
)
from .cout_dtos import (
    CoutEmployeDTO,
    CoutMaterielDTO,
    CoutMainOeuvreSummaryDTO,
    CoutMaterielSummaryDTO,
)
from .alerte_dtos import (
    AlerteCreateDTO,
    AlerteDTO,
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
    "AvenantCreateDTO",
    "AvenantUpdateDTO",
    "AvenantDTO",
    "SituationCreateDTO",
    "SituationUpdateDTO",
    "SituationDTO",
    "LigneSituationCreateDTO",
    "LigneSituationDTO",
    "FactureCreateDTO",
    "FactureUpdateDTO",
    "FactureDTO",
    "CoutEmployeDTO",
    "CoutMaterielDTO",
    "CoutMainOeuvreSummaryDTO",
    "CoutMaterielSummaryDTO",
    "AlerteCreateDTO",
    "AlerteDTO",
    "KPIFinancierDTO",
    "DerniersAchatsDTO",
    "DashboardFinancierDTO",
]
