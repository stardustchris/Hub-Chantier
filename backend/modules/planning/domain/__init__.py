"""Domain Layer du module planning.

Ce module contient la logique metier pure pour le planning operationnel :
- Entites (Affectation)
- Value Objects (HeureAffectation, TypeAffectation, JourSemaine)
- Interfaces Repository (AffectationRepository)
- Domain Events (AffectationCreatedEvent, etc.)

Selon CDC Section 5 - Planning Operationnel (PLN-01 a PLN-28).

REGLE : Aucune dependance vers des frameworks externes.
"""

from .entities import Affectation
from .value_objects import HeureAffectation, TypeAffectation, JourSemaine
from .repositories import AffectationRepository
from .events import (
    AffectationCreatedEvent,
    AffectationUpdatedEvent,
    AffectationDeletedEvent,
)

__all__ = [
    # Entities
    "Affectation",
    # Value Objects
    "HeureAffectation",
    "TypeAffectation",
    "JourSemaine",
    # Repositories
    "AffectationRepository",
    # Events
    "AffectationCreatedEvent",
    "AffectationUpdatedEvent",
    "AffectationDeletedEvent",
]
