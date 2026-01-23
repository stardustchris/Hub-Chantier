"""Application Layer du module Taches - CDC Section 13."""

from .dtos import (
    TacheDTO,
    CreateTacheDTO,
    UpdateTacheDTO,
    TacheListDTO,
    TacheStatsDTO,
    TemplateModeleDTO,
    CreateTemplateModeleDTO,
    UpdateTemplateModeleDTO,
    TemplateModeleListDTO,
    SousTacheModeleDTO,
    FeuilleTacheDTO,
    CreateFeuilleTacheDTO,
    UpdateFeuilleTacheDTO,
    FeuilleTacheListDTO,
    ValidateFeuilleTacheDTO,
)

from .use_cases import (
    # Tache Use Cases
    CreateTacheUseCase,
    UpdateTacheUseCase,
    DeleteTacheUseCase,
    GetTacheUseCase,
    ListTachesUseCase,
    CompleteTacheUseCase,
    ReorderTachesUseCase,
    # Template Use Cases
    CreateTemplateUseCase,
    ListTemplatesUseCase,
    ImportTemplateUseCase,
    # Feuille Tache Use Cases
    CreateFeuilleTacheUseCase,
    ValidateFeuilleTacheUseCase,
    ListFeuillesTachesUseCase,
    # Stats
    GetTacheStatsUseCase,
    # Export
    ExportTachesPDFUseCase,
    # Errors
    TacheNotFoundError,
    TacheAlreadyExistsError,
    TemplateNotFoundError,
    TemplateAlreadyExistsError,
    FeuilleTacheNotFoundError,
    FeuilleTacheAlreadyExistsError,
)

__all__ = [
    # DTOs
    "TacheDTO",
    "CreateTacheDTO",
    "UpdateTacheDTO",
    "TacheListDTO",
    "TacheStatsDTO",
    "TemplateModeleDTO",
    "CreateTemplateModeleDTO",
    "UpdateTemplateModeleDTO",
    "TemplateModeleListDTO",
    "SousTacheModeleDTO",
    "FeuilleTacheDTO",
    "CreateFeuilleTacheDTO",
    "UpdateFeuilleTacheDTO",
    "FeuilleTacheListDTO",
    "ValidateFeuilleTacheDTO",
    # Use Cases
    "CreateTacheUseCase",
    "UpdateTacheUseCase",
    "DeleteTacheUseCase",
    "GetTacheUseCase",
    "ListTachesUseCase",
    "CompleteTacheUseCase",
    "ReorderTachesUseCase",
    "CreateTemplateUseCase",
    "ListTemplatesUseCase",
    "ImportTemplateUseCase",
    "CreateFeuilleTacheUseCase",
    "ValidateFeuilleTacheUseCase",
    "ListFeuillesTachesUseCase",
    "GetTacheStatsUseCase",
    "ExportTachesPDFUseCase",
    # Errors
    "TacheNotFoundError",
    "TacheAlreadyExistsError",
    "TemplateNotFoundError",
    "TemplateAlreadyExistsError",
    "FeuilleTacheNotFoundError",
    "FeuilleTacheAlreadyExistsError",
]
