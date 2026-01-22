"""Ports du module planning - Interfaces pour les services externes."""

from .event_bus import EventBus, NullEventBus

__all__ = [
    "EventBus",
    "NullEventBus",
]
