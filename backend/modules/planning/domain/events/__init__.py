"""Événements de domaine pour le module planning.

NOTE ARCHITECTURE : Deux styles d'événements coexistent.

- Style ancien (frozen dataclass) : utilisé par les use cases et les tests.
  Fichier : affectation_events.py
  Ces événements sont publiés en interne par les use cases via le port EventBus.

- Style nouveau (DomainEvent) : utilisé par les routes HTTP pour le EventBus partagé.
  Fichiers : affectation_created.py, affectation_updated.py, etc.
  Ces événements passent par event_bus.publish() avec event_type='affectation.created'.

Les handlers downstream (ex: pointages/event_handlers.py) utilisent _extract_event_field()
pour être compatibles avec les deux styles.
"""

# Old-style events (compatible with existing use cases and tests)
from .affectation_events import (
    AffectationCreatedEvent,
    AffectationUpdatedEvent,
    AffectationDeletedEvent,
    AffectationBulkCreatedEvent,
    AffectationBulkDeletedEvent,
)

# New DomainEvent-based events (used by routes for shared EventBus)
from .affectation_cancelled import AffectationCancelledEvent

__all__ = [
    "AffectationCreatedEvent",
    "AffectationUpdatedEvent",
    "AffectationDeletedEvent",
    "AffectationCancelledEvent",
    "AffectationBulkCreatedEvent",
    "AffectationBulkDeletedEvent",
]
