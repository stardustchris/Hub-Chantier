"""Use Cases du module planning."""

from .create_affectation import CreateAffectationUseCase
from .update_affectation import UpdateAffectationUseCase
from .delete_affectation import DeleteAffectationUseCase
from .get_planning import GetPlanningUseCase
from .duplicate_affectations import DuplicateAffectationsUseCase
from .get_non_planifies import GetNonPlanifiesUseCase
from .exceptions import (
    AffectationConflictError,
    AffectationNotFoundError,
    InvalidDateRangeError,
    NoAffectationsToDuplicateError,
)

__all__ = [
    # Use Cases
    "CreateAffectationUseCase",
    "UpdateAffectationUseCase",
    "DeleteAffectationUseCase",
    "GetPlanningUseCase",
    "DuplicateAffectationsUseCase",
    "GetNonPlanifiesUseCase",
    # Exceptions
    "AffectationConflictError",
    "AffectationNotFoundError",
    "InvalidDateRangeError",
    "NoAffectationsToDuplicateError",
]
