"""Infrastructure Layer du module Planning.

Ce module contient les implementations techniques :
- Persistence (SQLAlchemy models et repositories)
- Event Bus implementation
- Web (routes FastAPI et dependances)

REGLE : Cette couche depend de toutes les autres.
"""

from .persistence import AffectationModel, Base, SQLAlchemyAffectationRepository
from .event_bus_impl import EventBusImpl, NoOpEventBus
from .web import router, get_planning_controller

__all__ = [
    # Persistence
    "AffectationModel",
    "Base",
    "SQLAlchemyAffectationRepository",
    # Event Bus
    "EventBusImpl",
    "NoOpEventBus",
    # Web
    "router",
    "get_planning_controller",
]
