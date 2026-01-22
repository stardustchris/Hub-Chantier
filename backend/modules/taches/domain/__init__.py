"""Domain Layer du module Taches - CDC Section 13."""

from .entities import Tache, TemplateModele, SousTacheModele, FeuilleTache
from .value_objects import StatutTache, UniteMesure, CouleurProgression
from .repositories import TacheRepository, TemplateModeleRepository, FeuilleTacheRepository
from .events import (
    TacheCreatedEvent,
    TacheUpdatedEvent,
    TacheDeletedEvent,
    TacheTermineeEvent,
    SousTacheAddedEvent,
    FeuilleTacheCreatedEvent,
    FeuilleTacheValidatedEvent,
    FeuilleTacheRejectedEvent,
    TachesImportedFromTemplateEvent,
)

__all__ = [
    # Entities
    "Tache",
    "TemplateModele",
    "SousTacheModele",
    "FeuilleTache",
    # Value Objects
    "StatutTache",
    "UniteMesure",
    "CouleurProgression",
    # Repositories
    "TacheRepository",
    "TemplateModeleRepository",
    "FeuilleTacheRepository",
    # Events
    "TacheCreatedEvent",
    "TacheUpdatedEvent",
    "TacheDeletedEvent",
    "TacheTermineeEvent",
    "SousTacheAddedEvent",
    "FeuilleTacheCreatedEvent",
    "FeuilleTacheValidatedEvent",
    "FeuilleTacheRejectedEvent",
    "TachesImportedFromTemplateEvent",
]
