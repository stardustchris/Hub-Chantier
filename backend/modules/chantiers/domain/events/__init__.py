"""Événements de domaine pour le module chantiers.

NOTE ARCHITECTURE : Deux styles d'événements coexistent.

- Style ancien (frozen dataclass) : chantier_events.py
  Utilisé par les use cases internes et les tests.

- Style nouveau (DomainEvent) : chantier_created.py, chantier_statut_changed.py, etc.
  Utilisé par les routes HTTP pour event_bus.publish() avec event_type='chantier.created'.

Les event handlers dans chantiers/infrastructure/event_handlers.py sont compatibles
avec les deux styles via lecture de event.data ou attributs directs.
"""

# Old-style events (compatible with existing use cases and tests)
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
