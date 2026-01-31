"""Ports de l'application Financier."""

from .event_bus import EventBus, NoOpEventBus

__all__ = ["EventBus", "NoOpEventBus"]
