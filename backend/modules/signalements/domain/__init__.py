"""Domain Layer du module Signalements."""

from .entities import Signalement, Reponse
from .value_objects import Priorite, StatutSignalement
from .repositories import SignalementRepository, ReponseRepository
from .services import EscaladeService
from .events import (
    SignalementCreated,
    SignalementUpdated,
    SignalementAssigned,
    SignalementStatusChanged,
    SignalementEscalated,
    ReponseAdded,
)

__all__ = [
    # Entities
    "Signalement",
    "Reponse",
    # Value Objects
    "Priorite",
    "StatutSignalement",
    # Repositories
    "SignalementRepository",
    "ReponseRepository",
    # Services
    "EscaladeService",
    # Events
    "SignalementCreated",
    "SignalementUpdated",
    "SignalementAssigned",
    "SignalementStatusChanged",
    "SignalementEscalated",
    "ReponseAdded",
]
