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
from .avenant_use_cases import (
    CreateAvenantUseCase,
    UpdateAvenantUseCase,
    ValiderAvenantUseCase,
    GetAvenantUseCase,
    ListAvenantsUseCase,
    DeleteAvenantUseCase,
    AvenantNotFoundError,
    AvenantAlreadyValideError,
)
from .situation_use_cases import (
    CreateSituationUseCase,
    UpdateSituationUseCase,
    SoumettreSituationUseCase,
    ValiderSituationUseCase,
    MarquerValideeClientUseCase,
    MarquerFactureeSituationUseCase,
    GetSituationUseCase,
    ListSituationsUseCase,
    DeleteSituationUseCase,
    SituationNotFoundError,
    SituationWorkflowError,
)
from .facture_use_cases import (
    CreateFactureFromSituationUseCase,
    CreateFactureAcompteUseCase,
    EmettreFactureUseCase,
    EnvoyerFactureUseCase,
    MarquerPayeeFactureUseCase,
    AnnulerFactureUseCase,
    GetFactureUseCase,
    ListFacturesUseCase,
    FactureNotFoundError,
    FactureWorkflowError,
    SituationNonValideeError,
)
from .cout_main_oeuvre_use_cases import GetCoutMainOeuvreUseCase
from .cout_materiel_use_cases import GetCoutMaterielUseCase
from .alerte_use_cases import (
    VerifierDepassementUseCase,
    AcquitterAlerteUseCase,
    ListAlertesUseCase,
    AlerteNotFoundError,
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
    # Avenant
    "CreateAvenantUseCase",
    "UpdateAvenantUseCase",
    "ValiderAvenantUseCase",
    "GetAvenantUseCase",
    "ListAvenantsUseCase",
    "DeleteAvenantUseCase",
    "AvenantNotFoundError",
    "AvenantAlreadyValideError",
    # Situation de Travaux
    "CreateSituationUseCase",
    "UpdateSituationUseCase",
    "SoumettreSituationUseCase",
    "ValiderSituationUseCase",
    "MarquerValideeClientUseCase",
    "MarquerFactureeSituationUseCase",
    "GetSituationUseCase",
    "ListSituationsUseCase",
    "DeleteSituationUseCase",
    "SituationNotFoundError",
    "SituationWorkflowError",
    # Facture Client
    "CreateFactureFromSituationUseCase",
    "CreateFactureAcompteUseCase",
    "EmettreFactureUseCase",
    "EnvoyerFactureUseCase",
    "MarquerPayeeFactureUseCase",
    "AnnulerFactureUseCase",
    "GetFactureUseCase",
    "ListFacturesUseCase",
    "FactureNotFoundError",
    "FactureWorkflowError",
    "SituationNonValideeError",
    # Couts
    "GetCoutMainOeuvreUseCase",
    "GetCoutMaterielUseCase",
    # Alertes
    "VerifierDepassementUseCase",
    "AcquitterAlerteUseCase",
    "ListAlertesUseCase",
    "AlerteNotFoundError",
    # Dashboard
    "GetDashboardFinancierUseCase",
]
