"""Web infrastructure du module Planning.

Ce module contient les routes FastAPI et dependances
pour le module Planning Operationnel.
"""

from .planning_routes import router
from .dependencies import (
    get_planning_controller,
    get_affectation_repository,
    get_event_bus,
    get_create_affectation_use_case,
    get_update_affectation_use_case,
    get_delete_affectation_use_case,
    get_get_planning_use_case,
    get_duplicate_affectations_use_case,
    get_get_non_planifies_use_case,
)

__all__ = [
    # Router
    "router",
    # Dependencies
    "get_planning_controller",
    "get_affectation_repository",
    "get_event_bus",
    "get_create_affectation_use_case",
    "get_update_affectation_use_case",
    "get_delete_affectation_use_case",
    "get_get_planning_use_case",
    "get_duplicate_affectations_use_case",
    "get_get_non_planifies_use_case",
]
