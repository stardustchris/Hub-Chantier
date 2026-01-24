"""DTOs pour le module Logistique."""
from .ressource_dto import (
    CreateRessourceDTO,
    UpdateRessourceDTO,
    RessourceDTO,
    RessourceListDTO,
)
from .reservation_dto import (
    CreateReservationDTO,
    ValidateReservationDTO,
    RefuseReservationDTO,
    ReservationFiltersDTO,
    ReservationDTO,
    ReservationListDTO,
    PlanningRessourceDTO,
    ConflitReservationDTO,
)

__all__ = [
    # Ressources
    "CreateRessourceDTO",
    "UpdateRessourceDTO",
    "RessourceDTO",
    "RessourceListDTO",
    # Reservations
    "CreateReservationDTO",
    "ValidateReservationDTO",
    "RefuseReservationDTO",
    "ReservationFiltersDTO",
    "ReservationDTO",
    "ReservationListDTO",
    "PlanningRessourceDTO",
    "ConflitReservationDTO",
]
