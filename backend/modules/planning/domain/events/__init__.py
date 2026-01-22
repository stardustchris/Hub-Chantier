"""Domain Events du module planning."""

from .affectation_events import (
    AffectationCreatedEvent,
    AffectationUpdatedEvent,
    AffectationDeletedEvent,
    AffectationBulkCreatedEvent,
    AffectationBulkDeletedEvent,
)

__all__ = [
    "AffectationCreatedEvent",
    "AffectationUpdatedEvent",
    "AffectationDeletedEvent",
    "AffectationBulkCreatedEvent",
    "AffectationBulkDeletedEvent",
]
