"""Adapters Layer du module Planning.

Ce module contient les adaptateurs qui font le pont entre
la couche Application et les technologies externes:
- Controllers (HTTP -> Use Cases)
- Presenters (Use Cases -> HTTP responses)
- Providers (services externes)

REGLE : Les dependances pointent vers l'interieur (Application layer).
"""

from .controllers import (
    PlanningController,
    CreateAffectationRequest,
    UpdateAffectationRequest,
    AffectationResponse,
    PlanningFiltersRequest,
    DuplicateAffectationsRequest,
    DeleteResponse,
    NonPlanifiesResponse,
)
from .presenters import AffectationPresenter

__all__ = [
    # Controller
    "PlanningController",
    # Presenter
    "AffectationPresenter",
    # Schemas
    "CreateAffectationRequest",
    "UpdateAffectationRequest",
    "AffectationResponse",
    "PlanningFiltersRequest",
    "DuplicateAffectationsRequest",
    "DeleteResponse",
    "NonPlanifiesResponse",
]
