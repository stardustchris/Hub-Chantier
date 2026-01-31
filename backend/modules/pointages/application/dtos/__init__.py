"""DTOs du module pointages."""

from .pointage_dtos import (
    CreatePointageDTO,
    UpdatePointageDTO,
    SignPointageDTO,
    ValidatePointageDTO,
    RejectPointageDTO,
    BulkCreatePointageDTO,
    AffectationSourceDTO,
    PointageDTO,
    PointageListDTO,
    PointageSearchDTO,
    CreateVariablePaieDTO,
    VariablePaieDTO,
)

from .feuille_heures_dtos import (
    CreateFeuilleHeuresDTO,
    FeuilleHeuresDTO,
    PointageJourDTO,
    VariablePaieSemaineDTO,
    FeuilleHeuresListDTO,
    FeuilleHeuresSearchDTO,
    NavigationSemaineDTO,
    VueChantierDTO,
    PointageUtilisateurDTO,
    VueCompagnonDTO,
    ChantierPointageDTO,
    PointageJourCompagnonDTO,
    ComparaisonEquipesDTO,
    EquipeStatsDTO,
    EcartDTO,
    JaugeAvancementDTO,
)

from .export_dtos import (
    FormatExport,
    ExportFeuilleHeuresDTO,
    ExportResultDTO,
    FeuilleRouteDTO,
    ChantierRouteDTO,
    ImportERPDTO,
    DonneeERPDTO,
    ImportResultDTO,
    MacroPaieDTO,
    CalculMacroPaieDTO,
    ResultatMacroPaieDTO,
)

from .bulk_validate_dtos import (
    BulkValidatePointagesDTO,
    BulkValidatePointagesResultDTO,
    PointageValidationResult,
)

from .monthly_recap_dtos import (
    GenerateMonthlyRecapDTO,
    MonthlyRecapDTO,
    WeeklySummary,
    VariablePaieSummary,
    AbsenceSummary,
)

from .lock_period_dtos import (
    LockMonthlyPeriodDTO,
    LockMonthlyPeriodResultDTO,
)

__all__ = [
    # Pointage DTOs
    "CreatePointageDTO",
    "UpdatePointageDTO",
    "SignPointageDTO",
    "ValidatePointageDTO",
    "RejectPointageDTO",
    "BulkCreatePointageDTO",
    "AffectationSourceDTO",
    "PointageDTO",
    "PointageListDTO",
    "PointageSearchDTO",
    "CreateVariablePaieDTO",
    "VariablePaieDTO",
    # Feuille d'heures DTOs
    "CreateFeuilleHeuresDTO",
    "FeuilleHeuresDTO",
    "PointageJourDTO",
    "VariablePaieSemaineDTO",
    "FeuilleHeuresListDTO",
    "FeuilleHeuresSearchDTO",
    "NavigationSemaineDTO",
    "VueChantierDTO",
    "PointageUtilisateurDTO",
    "VueCompagnonDTO",
    "ChantierPointageDTO",
    "PointageJourCompagnonDTO",
    "ComparaisonEquipesDTO",
    "EquipeStatsDTO",
    "EcartDTO",
    "JaugeAvancementDTO",
    # Export DTOs
    "FormatExport",
    "ExportFeuilleHeuresDTO",
    "ExportResultDTO",
    "FeuilleRouteDTO",
    "ChantierRouteDTO",
    "ImportERPDTO",
    "DonneeERPDTO",
    "ImportResultDTO",
    "MacroPaieDTO",
    "CalculMacroPaieDTO",
    "ResultatMacroPaieDTO",
    # Bulk validation DTOs (GAP-FDH-004)
    "BulkValidatePointagesDTO",
    "BulkValidatePointagesResultDTO",
    "PointageValidationResult",
    # Monthly recap DTOs (GAP-FDH-008)
    "GenerateMonthlyRecapDTO",
    "MonthlyRecapDTO",
    "WeeklySummary",
    "VariablePaieSummary",
    "AbsenceSummary",
    # Lock period DTOs (GAP-FDH-009)
    "LockMonthlyPeriodDTO",
    "LockMonthlyPeriodResultDTO",
]
