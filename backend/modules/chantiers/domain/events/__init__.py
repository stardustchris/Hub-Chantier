"""Événements de domaine pour le module chantiers."""

# Use old-style events from chantier_events.py (compatible with existing use cases)
from .chantier_events import (
    ChantierCreatedEvent,
    ChantierUpdatedEvent,
    ChantierStatutChangedEvent,
    ChantierDeletedEvent,
    ConducteurAssigneEvent,
    ChefChantierAssigneEvent,
)

__all__ = [
    "ChantierCreatedEvent",
    "ChantierUpdatedEvent",
    "ChantierStatutChangedEvent",
    "ChantierDeletedEvent",
    "ConducteurAssigneEvent",
    "ChefChantierAssigneEvent",
]
