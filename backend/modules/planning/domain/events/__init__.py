"""Événements de domaine pour le module planning."""

# Use old-style events from affectation_events.py (compatible with existing use cases)
from .affectation_events import (
    AffectationCreatedEvent,
    AffectationUpdatedEvent,
    AffectationDeletedEvent,
    AffectationBulkCreatedEvent,
    AffectationBulkDeletedEvent,
)

# New DomainEvent-based events (for Phase 2 refactoring)
from .affectation_cancelled import AffectationCancelledEvent

__all__ = [
    "AffectationCreatedEvent",
    "AffectationUpdatedEvent",
    "AffectationDeletedEvent",
    "AffectationCancelledEvent",
    "AffectationBulkCreatedEvent",
    "AffectationBulkDeletedEvent",
]
