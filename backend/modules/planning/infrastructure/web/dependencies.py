"""Dependances FastAPI pour le module planning."""

from typing import Dict, Any, List, Optional, Callable
from fastapi import Depends
from sqlalchemy.orm import Session

from ...adapters.controllers import PlanningController
from ...application.use_cases import (
    CreateAffectationUseCase,
    UpdateAffectationUseCase,
    DeleteAffectationUseCase,
    GetPlanningUseCase,
    DuplicateAffectationsUseCase,
    GetNonPlanifiesUseCase,
)
from ..persistence import SQLAlchemyAffectationRepository
from ..event_bus_impl import EventBusImpl, NoOpEventBus
from shared.infrastructure.database import get_db


def get_affectation_repository(
    db: Session = Depends(get_db),
) -> SQLAlchemyAffectationRepository:
    """
    Retourne le repository des affectations.

    Args:
        db: Session SQLAlchemy injectee.

    Returns:
        Instance du repository.
    """
    return SQLAlchemyAffectationRepository(db)


def get_event_bus() -> EventBusImpl:
    """
    Retourne l'implementation de l'EventBus.

    Returns:
        Instance de l'EventBus (NoOp pour l'instant).
    """
    # Pour l'instant, on utilise NoOpEventBus pour simplifier
    # On peut activer le CoreEventBus plus tard
    return NoOpEventBus()


def _get_user_info_func(db: Session) -> Callable[[int], Dict[str, Any]]:
    """
    Cree une fonction pour recuperer les infos utilisateur.

    Args:
        db: Session SQLAlchemy.

    Returns:
        Fonction qui prend un user_id et retourne ses infos.
    """
    def get_user_info(user_id: int) -> Dict[str, Any]:
        """Recupere nom, couleur, metier d'un utilisateur."""
        try:
            from modules.auth.infrastructure.persistence import SQLAlchemyUserRepository
            user_repo = SQLAlchemyUserRepository(db)
            user = user_repo.find_by_id(user_id)
            if user:
                return {
                    "nom": f"{user.prenom.value} {user.nom.value}",
                    "couleur": user.couleur.value if user.couleur else None,
                    "metier": user.metier,
                }
        except Exception:
            pass
        return {}

    return get_user_info


def _get_chantier_info_func(db: Session) -> Callable[[int], Dict[str, Any]]:
    """
    Cree une fonction pour recuperer les infos chantier.

    Args:
        db: Session SQLAlchemy.

    Returns:
        Fonction qui prend un chantier_id et retourne ses infos.
    """
    def get_chantier_info(chantier_id: int) -> Dict[str, Any]:
        """Recupere nom, couleur d'un chantier."""
        try:
            from modules.chantiers.infrastructure.persistence import SQLAlchemyChantierRepository
            chantier_repo = SQLAlchemyChantierRepository(db)
            chantier = chantier_repo.find_by_id(chantier_id)
            if chantier:
                return {
                    "nom": chantier.nom,
                    "couleur": chantier.couleur.value if chantier.couleur else None,
                }
        except Exception:
            pass
        return {}

    return get_chantier_info


def _get_user_chantiers_func(db: Session) -> Callable[[int], List[int]]:
    """
    Cree une fonction pour recuperer les chantiers d'un chef.

    Args:
        db: Session SQLAlchemy.

    Returns:
        Fonction qui prend un user_id et retourne ses chantiers.
    """
    def get_user_chantiers(user_id: int) -> List[int]:
        """Recupere les IDs des chantiers dont l'utilisateur est responsable."""
        try:
            from modules.chantiers.infrastructure.persistence import SQLAlchemyChantierRepository
            chantier_repo = SQLAlchemyChantierRepository(db)
            chantiers = chantier_repo.find_by_responsable(user_id)
            return [c.id for c in chantiers]
        except Exception:
            pass
        return []

    return get_user_chantiers


def _get_active_user_ids_func(db: Session) -> Callable[[], List[int]]:
    """
    Cree une fonction pour recuperer les IDs des utilisateurs actifs.

    Args:
        db: Session SQLAlchemy.

    Returns:
        Fonction qui retourne les IDs des utilisateurs actifs.
    """
    def get_active_user_ids() -> List[int]:
        """Recupere les IDs de tous les utilisateurs actifs."""
        try:
            from modules.auth.infrastructure.persistence import SQLAlchemyUserRepository
            user_repo = SQLAlchemyUserRepository(db)
            users = user_repo.find_active()
            return [u.id for u in users]
        except Exception:
            pass
        return []

    return get_active_user_ids


def get_create_affectation_use_case(
    affectation_repo: SQLAlchemyAffectationRepository = Depends(get_affectation_repository),
    event_bus: EventBusImpl = Depends(get_event_bus),
) -> CreateAffectationUseCase:
    """Retourne le use case de creation d'affectation."""
    return CreateAffectationUseCase(
        affectation_repo=affectation_repo,
        event_bus=event_bus,
    )


def get_update_affectation_use_case(
    affectation_repo: SQLAlchemyAffectationRepository = Depends(get_affectation_repository),
    event_bus: EventBusImpl = Depends(get_event_bus),
) -> UpdateAffectationUseCase:
    """Retourne le use case de mise a jour d'affectation."""
    return UpdateAffectationUseCase(
        affectation_repo=affectation_repo,
        event_bus=event_bus,
    )


def get_delete_affectation_use_case(
    affectation_repo: SQLAlchemyAffectationRepository = Depends(get_affectation_repository),
    event_bus: EventBusImpl = Depends(get_event_bus),
) -> DeleteAffectationUseCase:
    """Retourne le use case de suppression d'affectation."""
    return DeleteAffectationUseCase(
        affectation_repo=affectation_repo,
        event_bus=event_bus,
    )


def get_get_planning_use_case(
    affectation_repo: SQLAlchemyAffectationRepository = Depends(get_affectation_repository),
    db: Session = Depends(get_db),
) -> GetPlanningUseCase:
    """Retourne le use case de recuperation du planning."""
    return GetPlanningUseCase(
        affectation_repo=affectation_repo,
        get_user_info=_get_user_info_func(db),
        get_chantier_info=_get_chantier_info_func(db),
        get_user_chantiers=_get_user_chantiers_func(db),
    )


def get_duplicate_affectations_use_case(
    affectation_repo: SQLAlchemyAffectationRepository = Depends(get_affectation_repository),
    event_bus: EventBusImpl = Depends(get_event_bus),
) -> DuplicateAffectationsUseCase:
    """Retourne le use case de duplication d'affectations."""
    return DuplicateAffectationsUseCase(
        affectation_repo=affectation_repo,
        event_bus=event_bus,
    )


def get_get_non_planifies_use_case(
    affectation_repo: SQLAlchemyAffectationRepository = Depends(get_affectation_repository),
    db: Session = Depends(get_db),
) -> GetNonPlanifiesUseCase:
    """Retourne le use case de recuperation des non planifies."""
    return GetNonPlanifiesUseCase(
        affectation_repo=affectation_repo,
        get_active_user_ids=_get_active_user_ids_func(db),
    )


def get_planning_controller(
    create_uc: CreateAffectationUseCase = Depends(get_create_affectation_use_case),
    update_uc: UpdateAffectationUseCase = Depends(get_update_affectation_use_case),
    delete_uc: DeleteAffectationUseCase = Depends(get_delete_affectation_use_case),
    get_planning_uc: GetPlanningUseCase = Depends(get_get_planning_use_case),
    duplicate_uc: DuplicateAffectationsUseCase = Depends(get_duplicate_affectations_use_case),
    get_non_planifies_uc: GetNonPlanifiesUseCase = Depends(get_get_non_planifies_use_case),
) -> PlanningController:
    """
    Retourne le controller du planning.

    Args:
        create_uc: Use case de creation.
        update_uc: Use case de mise a jour.
        delete_uc: Use case de suppression.
        get_planning_uc: Use case de recuperation.
        duplicate_uc: Use case de duplication.
        get_non_planifies_uc: Use case des non planifies.

    Returns:
        Instance du PlanningController.
    """
    return PlanningController(
        create_affectation_uc=create_uc,
        update_affectation_uc=update_uc,
        delete_affectation_uc=delete_uc,
        get_planning_uc=get_planning_uc,
        duplicate_affectations_uc=duplicate_uc,
        get_non_planifies_uc=get_non_planifies_uc,
    )
