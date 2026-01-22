"""Application Layer du module planning.

Ce module contient la logique applicative :
- Use Cases (Create, Update, Delete, GetPlanning, Duplicate, GetNonPlanifies)
- DTOs (CreateAffectationDTO, UpdateAffectationDTO, AffectationDTO, etc.)
- Ports (EventBus interface)

REGLE : Depend uniquement du Domain, pas de l'Infrastructure.

Selon CDC Section 5 - Planning Operationnel (PLN-01 a PLN-28).
"""

from .use_cases import (
    CreateAffectationUseCase,
    UpdateAffectationUseCase,
    DeleteAffectationUseCase,
    GetPlanningUseCase,
    DuplicateAffectationsUseCase,
    GetNonPlanifiesUseCase,
    AffectationConflictError,
    AffectationNotFoundError,
    InvalidDateRangeError,
    NoAffectationsToDuplicateError,
)
from .dtos import (
    CreateAffectationDTO,
    UpdateAffectationDTO,
    AffectationDTO,
    AffectationListDTO,
    PlanningFiltersDTO,
    DuplicateAffectationsDTO,
)
from .ports import EventBus, NullEventBus

__all__ = [
    # Use Cases
    "CreateAffectationUseCase",
    "UpdateAffectationUseCase",
    "DeleteAffectationUseCase",
    "GetPlanningUseCase",
    "DuplicateAffectationsUseCase",
    "GetNonPlanifiesUseCase",
    # DTOs
    "CreateAffectationDTO",
    "UpdateAffectationDTO",
    "AffectationDTO",
    "AffectationListDTO",
    "PlanningFiltersDTO",
    "DuplicateAffectationsDTO",
    # Ports
    "EventBus",
    "NullEventBus",
    # Exceptions
    "AffectationConflictError",
    "AffectationNotFoundError",
    "InvalidDateRangeError",
    "NoAffectationsToDuplicateError",
]
