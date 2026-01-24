"""Events du module Logistique."""

from .logistique_events import (
    RessourceCreatedEvent,
    RessourceUpdatedEvent,
    RessourceDeletedEvent,
    ReservationCreatedEvent,
    ReservationValideeEvent,
    ReservationRefuseeEvent,
    ReservationAnnuleeEvent,
    ReservationRappelEvent,
    ReservationConflitEvent,
)

__all__ = [
    "RessourceCreatedEvent",
    "RessourceUpdatedEvent",
    "RessourceDeletedEvent",
    "ReservationCreatedEvent",
    "ReservationValideeEvent",
    "ReservationRefuseeEvent",
    "ReservationAnnuleeEvent",
    "ReservationRappelEvent",
    "ReservationConflitEvent",
]
