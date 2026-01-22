"""Domain layer du module Chantiers.

Ce module contient les entités, value objects, interfaces repository
et événements du domaine. AUCUNE dépendance technique (FastAPI, SQLAlchemy, etc.).
"""

from .entities import Chantier
from .value_objects import (
    StatutChantier,
    StatutChantierEnum,
    CoordonneesGPS,
    CodeChantier,
    ContactChantier,
)
from .repositories import ChantierRepository
from .events import (
    ChantierCreatedEvent,
    ChantierUpdatedEvent,
    ChantierStatutChangedEvent,
    ChantierDeletedEvent,
    ConducteurAssigneEvent,
    ChefChantierAssigneEvent,
)

__all__ = [
    # Entities
    "Chantier",
    # Value Objects
    "StatutChantier",
    "StatutChantierEnum",
    "CoordonneesGPS",
    "CodeChantier",
    "ContactChantier",
    # Repository
    "ChantierRepository",
    # Events
    "ChantierCreatedEvent",
    "ChantierUpdatedEvent",
    "ChantierStatutChangedEvent",
    "ChantierDeletedEvent",
    "ConducteurAssigneEvent",
    "ChefChantierAssigneEvent",
]
