"""Événements de domaine pour le module planning."""

from .affectation_created import AffectationCreatedEvent
from .affectation_updated import AffectationUpdatedEvent
from .affectation_deleted import AffectationDeletedEvent
from .affectation_events import AffectationBulkCreatedEvent, AffectationBulkDeletedEvent

__all__ = [
    "AffectationCreatedEvent",
    "AffectationUpdatedEvent",
    "AffectationDeletedEvent",
    "AffectationBulkCreatedEvent",
    "AffectationBulkDeletedEvent",
]
