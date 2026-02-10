"""Domain layer partagé."""

from .value_objects import CouleurProgression
from .events import DomainEvent

__all__ = [
    "CouleurProgression",
    "DomainEvent",
]
