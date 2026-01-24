"""Use cases pour le module Logistique."""
from .ressource_use_cases import (
    CreateRessourceUseCase,
    GetRessourceUseCase,
    ListRessourcesUseCase,
    UpdateRessourceUseCase,
    DeleteRessourceUseCase,
    ActivateRessourceUseCase,
    RessourceNotFoundError,
    RessourceCodeAlreadyExistsError,
    AccessDeniedError,
)
from .reservation_use_cases import (
    CreateReservationUseCase,
    GetReservationUseCase,
    ListReservationsUseCase,
    ValidateReservationUseCase,
    RefuseReservationUseCase,
    CancelReservationUseCase,
    GetPlanningRessourceUseCase,
    GetPendingReservationsUseCase,
    CheckConflitsUseCase,
    ReservationNotFoundError,
    ConflitReservationError,
    InvalidStatusTransitionError,
)

__all__ = [
    # Ressource use cases
    "CreateRessourceUseCase",
    "GetRessourceUseCase",
    "ListRessourcesUseCase",
    "UpdateRessourceUseCase",
    "DeleteRessourceUseCase",
    "ActivateRessourceUseCase",
    # Reservation use cases
    "CreateReservationUseCase",
    "GetReservationUseCase",
    "ListReservationsUseCase",
    "ValidateReservationUseCase",
    "RefuseReservationUseCase",
    "CancelReservationUseCase",
    "GetPlanningRessourceUseCase",
    "GetPendingReservationsUseCase",
    "CheckConflitsUseCase",
    # Exceptions
    "RessourceNotFoundError",
    "RessourceCodeAlreadyExistsError",
    "AccessDeniedError",
    "ReservationNotFoundError",
    "ConflitReservationError",
    "InvalidStatusTransitionError",
]
