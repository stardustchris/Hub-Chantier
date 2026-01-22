"""Infrastructure Layer du module pointages.

Contient les implémentations techniques: persistence SQLAlchemy,
routes FastAPI, et bus d'événements.
"""

from .persistence import (
    PointageModel,
    FeuilleHeuresModel,
    VariablePaieModel,
    SQLAlchemyPointageRepository,
    SQLAlchemyFeuilleHeuresRepository,
    SQLAlchemyVariablePaieRepository,
)
from .web import router
from .event_bus_impl import EventBusImpl, get_event_bus

__all__ = [
    # Models
    "PointageModel",
    "FeuilleHeuresModel",
    "VariablePaieModel",
    # Repositories
    "SQLAlchemyPointageRepository",
    "SQLAlchemyFeuilleHeuresRepository",
    "SQLAlchemyVariablePaieRepository",
    # Web
    "router",
    # EventBus
    "EventBusImpl",
    "get_event_bus",
]
