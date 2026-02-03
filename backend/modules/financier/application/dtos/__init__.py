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
from .evolution_dtos import (
    EvolutionMensuelleDTO,
    EvolutionFinanciereDTO,
)
from .consolidation_dtos import (
    ChantierFinancierSummaryDTO,
    KPIGlobauxDTO,
    VueConsolideeDTO,
)
from .suggestions_dtos import (
    SuggestionDTO,
    IndicateursPredictifDTO,
    SuggestionsFinancieresDTO,
)
from .affectation_dtos import (
    CreateAffectationDTO,
    AffectationBudgetTacheDTO,
    AffectationAvecDetailsDTO,
)
from .export_dtos import (
    LigneExportComptableDTO,
    ExportComptableDTO,
)
from .bilan_cloture_dtos import (
    EcartLotDTO,
    BilanClotureDTO,
)
from .pnl_dtos import (
    LignePnLDTO,
    PnLChantierDTO,
)
# CONN-10 to CONN-17: Pennylane Inbound DTOs
from .pennylane_dtos import (
    PennylaneSyncResultDTO,
    PennylaneSyncHistoryDTO,
    PennylanePendingReconciliationDTO,
    PennylaneMappingDTO,
    PendingReconciliationListDTO,
    CreateMappingDTO,
    ResolveReconciliationDTO,
    TriggerSyncDTO,
    PennylaneDashboardDTO,
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
    "EvolutionMensuelleDTO",
    "EvolutionFinanciereDTO",
    # Consolidation (FIN-20)
    "ChantierFinancierSummaryDTO",
    "KPIGlobauxDTO",
    "VueConsolideeDTO",
    # Suggestions (FIN-21/22)
    "SuggestionDTO",
    "IndicateursPredictifDTO",
    "SuggestionsFinancieresDTO",
    # Affectation (FIN-03)
    "CreateAffectationDTO",
    "AffectationBudgetTacheDTO",
    "AffectationAvecDetailsDTO",
    # Export comptable (FIN-13)
    "LigneExportComptableDTO",
    "ExportComptableDTO",
    # Bilan de cloture (GAP #10)
    "EcartLotDTO",
    "BilanClotureDTO",
    # P&L (GAP #9)
    "LignePnLDTO",
    "PnLChantierDTO",
    # Pennylane Inbound (CONN-10 to CONN-17)
    "PennylaneSyncResultDTO",
    "PennylaneSyncHistoryDTO",
    "PennylanePendingReconciliationDTO",
    "PennylaneMappingDTO",
    "PendingReconciliationListDTO",
    "CreateMappingDTO",
    "ResolveReconciliationDTO",
    "TriggerSyncDTO",
    "PennylaneDashboardDTO",
]
