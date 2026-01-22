"""Application layer du module Chantiers.

Ce module contient les use cases (logique métier applicative)
et les DTOs pour le transfert de données.
"""

from .dtos import (
    ChantierDTO,
    ChantierListDTO,
    CreateChantierDTO,
    UpdateChantierDTO,
    ChangeStatutDTO,
    AssignResponsableDTO,
)
from .use_cases import (
    CreateChantierUseCase,
    GetChantierUseCase,
    ListChantiersUseCase,
    UpdateChantierUseCase,
    DeleteChantierUseCase,
    ChangeStatutUseCase,
    AssignResponsableUseCase,
    CodeChantierAlreadyExistsError,
    InvalidDatesError,
    ChantierNotFoundError,
    ChantierFermeError,
    ChantierActifError,
    TransitionNonAutoriseeError,
    InvalidRoleTypeError,
)

__all__ = [
    # DTOs
    "ChantierDTO",
    "ChantierListDTO",
    "CreateChantierDTO",
    "UpdateChantierDTO",
    "ChangeStatutDTO",
    "AssignResponsableDTO",
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
