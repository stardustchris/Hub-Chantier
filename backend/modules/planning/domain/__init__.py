"""Domain layer du module Planning."""

from .entities import Affectation
from .value_objects import CreneauHoraire, TypeRecurrence
from .repositories import AffectationRepository
from .events import (
    AffectationCreatedEvent,
    AffectationUpdatedEvent,
    AffectationDeletedEvent,
    AffectationsDupliquéesEvent,
)

__all__ = [
    # Entities
    "Affectation",
    # Value Objects
    "CreneauHoraire",
    "TypeRecurrence",
    # Repositories
    "AffectationRepository",
    # Events
    "AffectationCreatedEvent",
    "AffectationUpdatedEvent",
    "AffectationDeletedEvent",
    "AffectationsDupliquéesEvent",
]
