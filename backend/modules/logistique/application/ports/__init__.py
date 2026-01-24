"""Ports de l'application Logistique."""

from .event_bus import EventBus, NoOpEventBus

__all__ = ["EventBus", "NoOpEventBus"]
