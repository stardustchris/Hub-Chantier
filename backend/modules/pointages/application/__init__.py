"""Application Layer du module pointages (feuilles d'heures).

Contient les use cases, DTOs et ports pour la logique applicative.
Selon CDC Section 7 - Feuilles d'heures (FDH-01 à FDH-20).
"""

from .use_cases import (
    CreatePointageUseCase,
    UpdatePointageUseCase,
    DeletePointageUseCase,
    SignPointageUseCase,
    SubmitPointageUseCase,
    ValidatePointageUseCase,
    RejectPointageUseCase,
    CorrectPointageUseCase,
    GetPointageUseCase,
    ListPointagesUseCase,
    GetFeuilleHeuresUseCase,
    ListFeuillesHeuresUseCase,
    GetVueSemaineUseCase,
    BulkCreateFromPlanningUseCase,
    CreateVariablePaieUseCase,
    ExportFeuilleHeuresUseCase,
    GetJaugeAvancementUseCase,
    CompareEquipesUseCase,
)

from .dtos import (
    CreatePointageDTO,
    UpdatePointageDTO,
    SignPointageDTO,
    ValidatePointageDTO,
    RejectPointageDTO,
    PointageDTO,
    PointageListDTO,
    PointageSearchDTO,
    CreateFeuilleHeuresDTO,
    FeuilleHeuresDTO,
    FeuilleHeuresListDTO,
    FeuilleHeuresSearchDTO,
    NavigationSemaineDTO,
    VueChantierDTO,
    VueCompagnonDTO,
    ExportFeuilleHeuresDTO,
    ExportResultDTO,
    FormatExport,
    JaugeAvancementDTO,
    ComparaisonEquipesDTO,
)

from .ports import EventBus, NullEventBus

__all__ = [
    # Use Cases
    "CreatePointageUseCase",
    "UpdatePointageUseCase",
    "DeletePointageUseCase",
    "SignPointageUseCase",
    "SubmitPointageUseCase",
    "ValidatePointageUseCase",
    "RejectPointageUseCase",
    "CorrectPointageUseCase",
    "GetPointageUseCase",
    "ListPointagesUseCase",
    "GetFeuilleHeuresUseCase",
    "ListFeuillesHeuresUseCase",
    "GetVueSemaineUseCase",
    "BulkCreateFromPlanningUseCase",
    "CreateVariablePaieUseCase",
    "ExportFeuilleHeuresUseCase",
    "GetJaugeAvancementUseCase",
    "CompareEquipesUseCase",
    # DTOs
    "CreatePointageDTO",
    "UpdatePointageDTO",
    "SignPointageDTO",
    "ValidatePointageDTO",
    "RejectPointageDTO",
    "PointageDTO",
    "PointageListDTO",
    "PointageSearchDTO",
    "CreateFeuilleHeuresDTO",
    "FeuilleHeuresDTO",
    "FeuilleHeuresListDTO",
    "FeuilleHeuresSearchDTO",
    "NavigationSemaineDTO",
    "VueChantierDTO",
    "VueCompagnonDTO",
    "ExportFeuilleHeuresDTO",
    "ExportResultDTO",
    "FormatExport",
    "JaugeAvancementDTO",
    "ComparaisonEquipesDTO",
    # Ports
    "EventBus",
    "NullEventBus",
]
