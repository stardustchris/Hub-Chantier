"""Ports du module pointages (interfaces pour les services externes)."""

from .event_bus import EventBus, NullEventBus
from .paie_externe import ClientPaieExternePort, ErreurPaieExterne

__all__ = [
    "EventBus",
    "NullEventBus",
    "ClientPaieExternePort",
    "ErreurPaieExterne",
]
