"""Use Cases du module Planning."""

from .create_affectation import (
    CreateAffectationUseCase,
    AffectationAlreadyExistsError,
    InvalidCreneauError,
)
from .get_affectation import GetAffectationUseCase, AffectationNotFoundError
from .list_affectations import ListAffectationsUseCase
from .update_affectation import UpdateAffectationUseCase
from .delete_affectation import DeleteAffectationUseCase
from .deplacer_affectation import DeplacerAffectationUseCase
from .dupliquer_affectations import DupliquerAffectationsUseCase

__all__ = [
    # Use Cases
    "CreateAffectationUseCase",
    "GetAffectationUseCase",
    "ListAffectationsUseCase",
    "UpdateAffectationUseCase",
    "DeleteAffectationUseCase",
    "DeplacerAffectationUseCase",
    "DupliquerAffectationsUseCase",
    # Exceptions
    "AffectationAlreadyExistsError",
    "AffectationNotFoundError",
    "InvalidCreneauError",
]
