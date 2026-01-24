"""Dependencies pour le module Logistique.

Injection de dependances FastAPI.
"""
from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from shared.infrastructure.database import get_db
from shared.infrastructure.web.dependencies import get_current_user_id, get_current_user_role

from ..persistence import (
    SQLAlchemyRessourceRepository,
    SQLAlchemyReservationRepository,
)
from ...application.use_cases import (
    # Ressource use cases
    CreateRessourceUseCase,
    GetRessourceUseCase,
    ListRessourcesUseCase,
    UpdateRessourceUseCase,
    DeleteRessourceUseCase,
    ActivateRessourceUseCase,
    # Reservation use cases
    CreateReservationUseCase,
    GetReservationUseCase,
    ListReservationsUseCase,
    ValidateReservationUseCase,
    RefuseReservationUseCase,
    CancelReservationUseCase,
    GetPlanningRessourceUseCase,
    GetPendingReservationsUseCase,
    CheckConflitsUseCase,
)


# ----- Repositories -----

def get_ressource_repository(
    db: Session = Depends(get_db),
) -> SQLAlchemyRessourceRepository:
    """Fournit le repository des ressources."""
    return SQLAlchemyRessourceRepository(db)


def get_reservation_repository(
    db: Session = Depends(get_db),
) -> SQLAlchemyReservationRepository:
    """Fournit le repository des reservations."""
    return SQLAlchemyReservationRepository(db)


# ----- Ressource Use Cases -----

def get_create_ressource_use_case(
    repo: SQLAlchemyRessourceRepository = Depends(get_ressource_repository),
) -> CreateRessourceUseCase:
    """Fournit le use case de creation de ressource."""
    return CreateRessourceUseCase(repo)


def get_ressource_use_case(
    repo: SQLAlchemyRessourceRepository = Depends(get_ressource_repository),
) -> GetRessourceUseCase:
    """Fournit le use case d'obtention de ressource."""
    return GetRessourceUseCase(repo)


def get_list_ressources_use_case(
    repo: SQLAlchemyRessourceRepository = Depends(get_ressource_repository),
) -> ListRessourcesUseCase:
    """Fournit le use case de liste des ressources."""
    return ListRessourcesUseCase(repo)


def get_update_ressource_use_case(
    repo: SQLAlchemyRessourceRepository = Depends(get_ressource_repository),
) -> UpdateRessourceUseCase:
    """Fournit le use case de mise a jour de ressource."""
    return UpdateRessourceUseCase(repo)


def get_delete_ressource_use_case(
    repo: SQLAlchemyRessourceRepository = Depends(get_ressource_repository),
) -> DeleteRessourceUseCase:
    """Fournit le use case de suppression de ressource."""
    return DeleteRessourceUseCase(repo)


def get_activate_ressource_use_case(
    repo: SQLAlchemyRessourceRepository = Depends(get_ressource_repository),
) -> ActivateRessourceUseCase:
    """Fournit le use case d'activation de ressource."""
    return ActivateRessourceUseCase(repo)


# ----- Reservation Use Cases -----

def get_create_reservation_use_case(
    reservation_repo: SQLAlchemyReservationRepository = Depends(get_reservation_repository),
    ressource_repo: SQLAlchemyRessourceRepository = Depends(get_ressource_repository),
) -> CreateReservationUseCase:
    """Fournit le use case de creation de reservation."""
    return CreateReservationUseCase(reservation_repo, ressource_repo)


def get_reservation_use_case(
    repo: SQLAlchemyReservationRepository = Depends(get_reservation_repository),
) -> GetReservationUseCase:
    """Fournit le use case d'obtention de reservation."""
    return GetReservationUseCase(repo)


def get_list_reservations_use_case(
    repo: SQLAlchemyReservationRepository = Depends(get_reservation_repository),
) -> ListReservationsUseCase:
    """Fournit le use case de liste des reservations."""
    return ListReservationsUseCase(repo)


def get_validate_reservation_use_case(
    repo: SQLAlchemyReservationRepository = Depends(get_reservation_repository),
) -> ValidateReservationUseCase:
    """Fournit le use case de validation de reservation."""
    return ValidateReservationUseCase(repo)


def get_refuse_reservation_use_case(
    repo: SQLAlchemyReservationRepository = Depends(get_reservation_repository),
) -> RefuseReservationUseCase:
    """Fournit le use case de refus de reservation."""
    return RefuseReservationUseCase(repo)


def get_cancel_reservation_use_case(
    repo: SQLAlchemyReservationRepository = Depends(get_reservation_repository),
) -> CancelReservationUseCase:
    """Fournit le use case d'annulation de reservation."""
    return CancelReservationUseCase(repo)


def get_planning_ressource_use_case(
    reservation_repo: SQLAlchemyReservationRepository = Depends(get_reservation_repository),
    ressource_repo: SQLAlchemyRessourceRepository = Depends(get_ressource_repository),
) -> GetPlanningRessourceUseCase:
    """Fournit le use case de planning de ressource."""
    return GetPlanningRessourceUseCase(reservation_repo, ressource_repo)


def get_pending_reservations_use_case(
    repo: SQLAlchemyReservationRepository = Depends(get_reservation_repository),
) -> GetPendingReservationsUseCase:
    """Fournit le use case des reservations en attente."""
    return GetPendingReservationsUseCase(repo)


def get_check_conflits_use_case(
    repo: SQLAlchemyReservationRepository = Depends(get_reservation_repository),
) -> CheckConflitsUseCase:
    """Fournit le use case de verification des conflits."""
    return CheckConflitsUseCase(repo)
