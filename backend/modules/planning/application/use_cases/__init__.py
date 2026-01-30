"""Use Cases du module planning."""

from .create_affectation import CreateAffectationUseCase
from .update_affectation import UpdateAffectationUseCase
from .update_affectation_note import UpdateAffectationNoteUseCase
from .delete_affectation import DeleteAffectationUseCase
from .get_planning import GetPlanningUseCase
from .duplicate_affectations import DuplicateAffectationsUseCase
from .get_non_planifies import GetNonPlanifiesUseCase
from .resize_affectation import ResizeAffectationUseCase
from .exceptions import (
    AffectationConflictError,
    AffectationNotFoundError,
    InvalidDateRangeError,
    NoAffectationsToDuplicateError,
)
from .charge import (
    CreateBesoinUseCase,
    UpdateBesoinUseCase,
    DeleteBesoinUseCase,
    GetPlanningChargeUseCase,
    GetBesoinsByChantierUseCase,
    GetOccupationDetailsUseCase,
    BesoinNotFoundError,
    BesoinAlreadyExistsError,
    InvalidSemaineRangeError,
)

__all__ = [
    # Use Cases - Affectations
    "CreateAffectationUseCase",
    "UpdateAffectationUseCase",
    "UpdateAffectationNoteUseCase",
    "DeleteAffectationUseCase",
    "GetPlanningUseCase",
    "DuplicateAffectationsUseCase",
    "GetNonPlanifiesUseCase",
    "ResizeAffectationUseCase",
    # Use Cases - Charge
    "CreateBesoinUseCase",
    "UpdateBesoinUseCase",
    "DeleteBesoinUseCase",
    "GetPlanningChargeUseCase",
    "GetBesoinsByChantierUseCase",
    "GetOccupationDetailsUseCase",
    # Exceptions - Affectations
    "AffectationConflictError",
    "AffectationNotFoundError",
    "InvalidDateRangeError",
    "NoAffectationsToDuplicateError",
    # Exceptions - Charge
    "BesoinNotFoundError",
    "BesoinAlreadyExistsError",
    "InvalidSemaineRangeError",
]
