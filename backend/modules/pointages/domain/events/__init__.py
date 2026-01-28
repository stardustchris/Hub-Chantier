"""Événements de domaine pour le module pointages."""

from .pointage_events import (
    PointageCreatedEvent,
    PointageUpdatedEvent,
    PointageSignedEvent,
    PointageSubmittedEvent,
    PointageValidatedEvent,
    PointageRejectedEvent,
    PointageDeletedEvent,
    PointageBulkCreatedEvent,
    FeuilleHeuresCreatedEvent,
    FeuilleHeuresExportedEvent,
    VariablePaieCreatedEvent,
)
from .heures_created import HeuresCreatedEvent
from .heures_updated import HeuresUpdatedEvent
from .heures_validated import HeuresValidatedEvent
from .heures_rejected import HeuresRejectedEvent

__all__ = [
    "PointageCreatedEvent",
    "PointageUpdatedEvent",
    "PointageSignedEvent",
    "PointageSubmittedEvent",
    "PointageValidatedEvent",
    "PointageRejectedEvent",
    "PointageDeletedEvent",
    "PointageBulkCreatedEvent",
    "FeuilleHeuresCreatedEvent",
    "FeuilleHeuresExportedEvent",
    "VariablePaieCreatedEvent",
    "HeuresCreatedEvent",
    "HeuresUpdatedEvent",
    "HeuresValidatedEvent",
    "HeuresRejectedEvent",
]
