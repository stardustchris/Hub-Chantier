"""Use Cases du module pointages (feuilles d'heures)."""

from .create_pointage import CreatePointageUseCase
from .update_pointage import UpdatePointageUseCase
from .delete_pointage import DeletePointageUseCase
from .sign_pointage import SignPointageUseCase
from .submit_pointage import SubmitPointageUseCase
from .validate_pointage import ValidatePointageUseCase
from .reject_pointage import RejectPointageUseCase
from .correct_pointage import CorrectPointageUseCase
from .get_pointage import GetPointageUseCase
from .list_pointages import ListPointagesUseCase
from .get_feuille_heures import GetFeuilleHeuresUseCase
from .list_feuilles_heures import ListFeuillesHeuresUseCase
from .get_vue_semaine import GetVueSemaineUseCase
from .bulk_create_from_planning import BulkCreateFromPlanningUseCase
from .create_variable_paie import CreateVariablePaieUseCase
from .export_feuille_heures import ExportFeuilleHeuresUseCase
from .get_jauge_avancement import GetJaugeAvancementUseCase
from .compare_equipes import CompareEquipesUseCase
from .bulk_validate_pointages import BulkValidatePointagesUseCase
from .generate_monthly_recap import GenerateMonthlyRecapUseCase
from .lock_monthly_period import LockMonthlyPeriodUseCase

__all__ = [
    # Pointage CRUD
    "CreatePointageUseCase",
    "UpdatePointageUseCase",
    "DeletePointageUseCase",
    "GetPointageUseCase",
    "ListPointagesUseCase",
    # Workflow validation
    "SignPointageUseCase",
    "SubmitPointageUseCase",
    "ValidatePointageUseCase",
    "RejectPointageUseCase",
    "CorrectPointageUseCase",
    # Feuilles d'heures
    "GetFeuilleHeuresUseCase",
    "ListFeuillesHeuresUseCase",
    "GetVueSemaineUseCase",
    # Planning integration
    "BulkCreateFromPlanningUseCase",
    # Variables de paie
    "CreateVariablePaieUseCase",
    # Export / Rapports
    "ExportFeuilleHeuresUseCase",
    "GetJaugeAvancementUseCase",
    "CompareEquipesUseCase",
    # Phase 2 GAPs
    "BulkValidatePointagesUseCase",  # GAP-FDH-004
    "GenerateMonthlyRecapUseCase",   # GAP-FDH-008
    "LockMonthlyPeriodUseCase",      # GAP-FDH-009
]
