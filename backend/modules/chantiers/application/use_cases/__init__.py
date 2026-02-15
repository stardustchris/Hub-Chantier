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
from .change_statut import (
    ChangeStatutUseCase,
    TransitionNonAutoriseeError,
    PrerequisReceptionNonRemplisError,  # GAP-CHT-001
)
from .assign_responsable import AssignResponsableUseCase, InvalidRoleTypeError
from .fermer_chantier import (
    FermerChantierUseCase,
    PrerequisClotureNonRemplisError,
    FermetureForceeNonAutoriseeError,
)

__all__ = [
    # Use Cases
    "CreateChantierUseCase",
    "GetChantierUseCase",
    "ListChantiersUseCase",
    "UpdateChantierUseCase",
    "DeleteChantierUseCase",
    "ChangeStatutUseCase",
    "AssignResponsableUseCase",
    "FermerChantierUseCase",
    # Exceptions
    "CodeChantierAlreadyExistsError",
    "InvalidDatesError",
    "ChantierNotFoundError",
    "ChantierFermeError",
    "ChantierActifError",
    "TransitionNonAutoriseeError",
    "PrerequisReceptionNonRemplisError",  # GAP-CHT-001
    "InvalidRoleTypeError",
    "PrerequisClotureNonRemplisError",
    "FermetureForceeNonAutoriseeError",
]
