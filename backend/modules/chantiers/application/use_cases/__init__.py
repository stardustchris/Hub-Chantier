"""Use Cases du module Chantiers."""

from .create_chantier import (
    CreateChantierUseCase,
    CodeChantierAlreadyExistsError,
    InvalidDatesError,
)
from .get_chantier import GetChantierUseCase, ChantierNotFoundError
from .list_chantiers import ListChantiersUseCase
from .update_chantier import UpdateChantierUseCase, ChantierFermeError
from .delete_chantier import DeleteChantierUseCase, ChantierActifError
from .change_statut import ChangeStatutUseCase, TransitionNonAutoriseeError
from .assign_responsable import AssignResponsableUseCase, InvalidRoleTypeError

__all__ = [
    # Use Cases
    "CreateChantierUseCase",
    "GetChantierUseCase",
    "ListChantiersUseCase",
    "UpdateChantierUseCase",
    "DeleteChantierUseCase",
    "ChangeStatutUseCase",
    "AssignResponsableUseCase",
    # Exceptions
    "CodeChantierAlreadyExistsError",
    "InvalidDatesError",
    "ChantierNotFoundError",
    "ChantierFermeError",
    "ChantierActifError",
    "TransitionNonAutoriseeError",
    "InvalidRoleTypeError",
]
