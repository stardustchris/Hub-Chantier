"""Ports du module pointages (interfaces pour les services externes)."""

from .event_bus import EventBus, NullEventBus

__all__ = [
    "EventBus",
    "NullEventBus",
]
