"""Événements de domaine du module Planning."""

from .affectation_events import (
    AffectationCreatedEvent,
    AffectationUpdatedEvent,
    AffectationDeletedEvent,
    AffectationsDupliquéesEvent,
)

__all__ = [
    "AffectationCreatedEvent",
    "AffectationUpdatedEvent",
    "AffectationDeletedEvent",
    "AffectationsDupliquéesEvent",
]
