"""
Module Taches - Gestion des Taches de Chantier.

Selon CDC Section 13 - Gestion des Taches (TAC-01 a TAC-20).

Ce module permet de:
- Creer et gerer des taches hierarchiques par chantier (TAC-01, TAC-02)
- Utiliser une bibliotheque de modeles reutilisables (TAC-04, TAC-05)
- Suivre l'avancement avec code couleur (TAC-20)
- Gerer les feuilles de taches pour declaration quotidienne (TAC-18)
- Valider les travaux declares (TAC-19)
"""

from .domain import (
    # Entities
    Tache,
    TemplateModele,
    FeuilleTache,
    # Value Objects
    StatutTache,
    UniteMesure,
    CouleurProgression,
    # Repositories (interfaces)
    TacheRepository,
    TemplateModeleRepository,
    FeuilleTacheRepository,
)

from .application import (
    # DTOs
    TacheDTO,
    CreateTacheDTO,
    UpdateTacheDTO,
    TacheListDTO,
    TacheStatsDTO,
    TemplateModeleDTO,
    FeuilleTacheDTO,
    # Use Cases
    CreateTacheUseCase,
    UpdateTacheUseCase,
    DeleteTacheUseCase,
    GetTacheUseCase,
    ListTachesUseCase,
    CompleteTacheUseCase,
    ImportTemplateUseCase,
    CreateFeuilleTacheUseCase,
    ValidateFeuilleTacheUseCase,
    # Errors
    TacheNotFoundError,
    TemplateNotFoundError,
    FeuilleTacheNotFoundError,
)

from .adapters import TacheController

from .infrastructure import (
    # Models
    TacheModel,
    TemplateModeleModel,
    FeuilleTacheModel,
    # Repositories
    SQLAlchemyTacheRepository,
    SQLAlchemyTemplateModeleRepository,
    SQLAlchemyFeuilleTacheRepository,
    # Router
    taches_router,
)

__all__ = [
    # Domain
    "Tache",
    "TemplateModele",
    "FeuilleTache",
    "StatutTache",
    "UniteMesure",
    "CouleurProgression",
    "TacheRepository",
    "TemplateModeleRepository",
    "FeuilleTacheRepository",
    # Application
    "TacheDTO",
    "CreateTacheDTO",
    "UpdateTacheDTO",
    "TacheListDTO",
    "TacheStatsDTO",
    "TemplateModeleDTO",
    "FeuilleTacheDTO",
    "CreateTacheUseCase",
    "UpdateTacheUseCase",
    "DeleteTacheUseCase",
    "GetTacheUseCase",
    "ListTachesUseCase",
    "CompleteTacheUseCase",
    "ImportTemplateUseCase",
    "CreateFeuilleTacheUseCase",
    "ValidateFeuilleTacheUseCase",
    "TacheNotFoundError",
    "TemplateNotFoundError",
    "FeuilleTacheNotFoundError",
    # Adapters
    "TacheController",
    # Infrastructure
    "TacheModel",
    "TemplateModeleModel",
    "FeuilleTacheModel",
    "SQLAlchemyTacheRepository",
    "SQLAlchemyTemplateModeleRepository",
    "SQLAlchemyFeuilleTacheRepository",
    "taches_router",
]
