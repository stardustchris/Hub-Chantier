"""Domain Layer du module pointages (feuilles d'heures).

Ce module contient la logique métier pure, sans dépendance technique.
Selon CDC Section 7 - Feuilles d'heures (FDH-01 à FDH-20).
"""

from .entities import Pointage, VariablePaie, FeuilleHeures
from .value_objects import StatutPointage, TypeVariablePaie, Duree, Couleur
from .repositories import (
    PointageRepository,
    FeuilleHeuresRepository,
    VariablePaieRepository,
)
from .events import (
    PointageCreatedEvent,
    PointageUpdatedEvent,
    PointageSignedEvent,
    PointageSubmittedEvent,
    PointageValidatedEvent,
    PointageRejectedEvent,
    PointageDeletedEvent,
    PointageBulkCreatedEvent,
    FeuilleHeuresCreatedEvent,
    FeuilleHeuresExportedEvent,
    VariablePaieCreatedEvent,
)

__all__ = [
    # Entities
    "Pointage",
    "VariablePaie",
    "FeuilleHeures",
    # Value Objects
    "StatutPointage",
    "TypeVariablePaie",
    "Duree",
    "Couleur",
    # Repositories
    "PointageRepository",
    "FeuilleHeuresRepository",
    "VariablePaieRepository",
    # Events
    "PointageCreatedEvent",
    "PointageUpdatedEvent",
    "PointageSignedEvent",
    "PointageSubmittedEvent",
    "PointageValidatedEvent",
    "PointageRejectedEvent",
    "PointageDeletedEvent",
    "PointageBulkCreatedEvent",
    "FeuilleHeuresCreatedEvent",
    "FeuilleHeuresExportedEvent",
    "VariablePaieCreatedEvent",
]
