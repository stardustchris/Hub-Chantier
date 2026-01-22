"""DTOs du module Taches."""

from .tache_dto import (
    TacheDTO,
    CreateTacheDTO,
    UpdateTacheDTO,
    TacheListDTO,
    TacheStatsDTO,
)
from .template_modele_dto import (
    TemplateModeleDTO,
    CreateTemplateModeleDTO,
    UpdateTemplateModeleDTO,
    TemplateModeleListDTO,
    SousTacheModeleDTO,
)
from .feuille_tache_dto import (
    FeuilleTacheDTO,
    CreateFeuilleTacheDTO,
    UpdateFeuilleTacheDTO,
    FeuilleTacheListDTO,
    ValidateFeuilleTacheDTO,
)

__all__ = [
    # Tache DTOs
    "TacheDTO",
    "CreateTacheDTO",
    "UpdateTacheDTO",
    "TacheListDTO",
    "TacheStatsDTO",
    # Template DTOs
    "TemplateModeleDTO",
    "CreateTemplateModeleDTO",
    "UpdateTemplateModeleDTO",
    "TemplateModeleListDTO",
    "SousTacheModeleDTO",
    # Feuille DTOs
    "FeuilleTacheDTO",
    "CreateFeuilleTacheDTO",
    "UpdateFeuilleTacheDTO",
    "FeuilleTacheListDTO",
    "ValidateFeuilleTacheDTO",
]
