"""Injection de dépendances pour le module Logistique."""

from fastapi import Depends
from sqlalchemy.orm import Session

from shared.infrastructure.database import get_db
from shared.infrastructure.event_bus import EventBus as CoreEventBus
from ...application.ports.event_bus import EventBus
from ..event_bus_impl import LogistiqueEventBus

from ...domain.repositories import RessourceRepository, ReservationRepository
from ....auth.domain.repositories import UserRepository
from ....auth.infrastructure.persistence import SQLAlchemyUserRepository
from ...application.use_cases import (
    CreateRessourceUseCase,
    UpdateRessourceUseCase,
    DeleteRessourceUseCase,
    GetRessourceUseCase,
    ListRessourcesUseCase,
    CreateReservationUseCase,
    UpdateReservationUseCase,
    ValiderReservationUseCase,
    RefuserReservationUseCase,
    AnnulerReservationUseCase,
    GetReservationUseCase,
    GetPlanningRessourceUseCase,
    GetHistoriqueRessourceUseCase,
    ListReservationsEnAttenteUseCase,
)
from ..persistence import SQLAlchemyRessourceRepository, SQLAlchemyReservationRepository


def get_event_bus() -> EventBus:
    """Retourne l'EventBus avec logging pour audit trail (H8)."""
    return LogistiqueEventBus(CoreEventBus)


def get_ressource_repository(
    db: Session = Depends(get_db),
) -> RessourceRepository:
    """Retourne le repository Ressource."""
    return SQLAlchemyRessourceRepository(db)


def get_reservation_repository(
    db: Session = Depends(get_db),
) -> ReservationRepository:
    """Retourne le repository Reservation."""
    return SQLAlchemyReservationRepository(db)


def get_user_repository(
    db: Session = Depends(get_db),
) -> UserRepository:
    """Retourne le repository User."""
    return SQLAlchemyUserRepository(db)


# Use Cases Ressources


def get_create_ressource_use_case(
    ressource_repository: RessourceRepository = Depends(get_ressource_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> CreateRessourceUseCase:
    """Retourne le use case CreateRessource."""
    return CreateRessourceUseCase(ressource_repository, event_bus)


def get_update_ressource_use_case(
    ressource_repository: RessourceRepository = Depends(get_ressource_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> UpdateRessourceUseCase:
    """Retourne le use case UpdateRessource."""
    return UpdateRessourceUseCase(ressource_repository, event_bus)


def get_delete_ressource_use_case(
    ressource_repository: RessourceRepository = Depends(get_ressource_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> DeleteRessourceUseCase:
    """Retourne le use case DeleteRessource."""
    return DeleteRessourceUseCase(ressource_repository, event_bus)


def get_get_ressource_use_case(
    ressource_repository: RessourceRepository = Depends(get_ressource_repository),
) -> GetRessourceUseCase:
    """Retourne le use case GetRessource."""
    return GetRessourceUseCase(ressource_repository)


def get_list_ressources_use_case(
    ressource_repository: RessourceRepository = Depends(get_ressource_repository),
) -> ListRessourcesUseCase:
    """Retourne le use case ListRessources."""
    return ListRessourcesUseCase(ressource_repository)


# Use Cases Reservations


def get_create_reservation_use_case(
    reservation_repository: ReservationRepository = Depends(get_reservation_repository),
    ressource_repository: RessourceRepository = Depends(get_ressource_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> CreateReservationUseCase:
    """Retourne le use case CreateReservation."""
    return CreateReservationUseCase(
        reservation_repository, ressource_repository, event_bus
    )


def get_update_reservation_use_case(
    reservation_repository: ReservationRepository = Depends(get_reservation_repository),
    ressource_repository: RessourceRepository = Depends(get_ressource_repository),
) -> UpdateReservationUseCase:
    """Retourne le use case UpdateReservation."""
    return UpdateReservationUseCase(reservation_repository, ressource_repository)


def get_valider_reservation_use_case(
    reservation_repository: ReservationRepository = Depends(get_reservation_repository),
    ressource_repository: RessourceRepository = Depends(get_ressource_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> ValiderReservationUseCase:
    """Retourne le use case ValiderReservation."""
    return ValiderReservationUseCase(
        reservation_repository, ressource_repository, event_bus
    )


def get_refuser_reservation_use_case(
    reservation_repository: ReservationRepository = Depends(get_reservation_repository),
    ressource_repository: RessourceRepository = Depends(get_ressource_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> RefuserReservationUseCase:
    """Retourne le use case RefuserReservation."""
    return RefuserReservationUseCase(
        reservation_repository, ressource_repository, event_bus
    )


def get_annuler_reservation_use_case(
    reservation_repository: ReservationRepository = Depends(get_reservation_repository),
    event_bus: EventBus = Depends(get_event_bus),
) -> AnnulerReservationUseCase:
    """Retourne le use case AnnulerReservation."""
    return AnnulerReservationUseCase(reservation_repository, event_bus)


def get_get_reservation_use_case(
    reservation_repository: ReservationRepository = Depends(get_reservation_repository),
    ressource_repository: RessourceRepository = Depends(get_ressource_repository),
) -> GetReservationUseCase:
    """Retourne le use case GetReservation."""
    return GetReservationUseCase(reservation_repository, ressource_repository)


def get_planning_ressource_use_case(
    reservation_repository: ReservationRepository = Depends(get_reservation_repository),
    ressource_repository: RessourceRepository = Depends(get_ressource_repository),
    user_repository: UserRepository = Depends(get_user_repository),
) -> GetPlanningRessourceUseCase:
    """Retourne le use case GetPlanningRessource."""
    return GetPlanningRessourceUseCase(reservation_repository, ressource_repository, user_repository)


def get_historique_ressource_use_case(
    reservation_repository: ReservationRepository = Depends(get_reservation_repository),
    ressource_repository: RessourceRepository = Depends(get_ressource_repository),
) -> GetHistoriqueRessourceUseCase:
    """Retourne le use case GetHistoriqueRessource."""
    return GetHistoriqueRessourceUseCase(reservation_repository, ressource_repository)


def get_list_reservations_en_attente_use_case(
    reservation_repository: ReservationRepository = Depends(get_reservation_repository),
    ressource_repository: RessourceRepository = Depends(get_ressource_repository),
) -> ListReservationsEnAttenteUseCase:
    """Retourne le use case ListReservationsEnAttente."""
    return ListReservationsEnAttenteUseCase(reservation_repository, ressource_repository)
