"""Dependances FastAPI pour le module planning.

Ce fichier configure l'injection de dependances pour le module planning.

ARCHITECTURE CLEAN RESPECTEE:
- AUCUN import direct vers d'autres modules (auth, chantiers)
- Utilise le service shared EntityInfoService pour les infos inter-modules
- EventBus actif pour la communication par evenements
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from ...adapters.controllers import PlanningController
from ...adapters.presenters import AffectationPresenter
from ...application.use_cases import (
    CreateAffectationUseCase,
    UpdateAffectationUseCase,
    DeleteAffectationUseCase,
    GetPlanningUseCase,
    DuplicateAffectationsUseCase,
    GetNonPlanifiesUseCase,
)
from ..persistence import SQLAlchemyAffectationRepository
from ..event_bus_impl import EventBusImpl
from shared.infrastructure.database import get_db
from shared.infrastructure.event_bus import EventBus as CoreEventBus
from shared.infrastructure import get_entity_info_service
from shared.application.ports import EntityInfoService


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
    Retourne l'implementation de l'EventBus ACTIVE.

    L'EventBus permet la communication inter-modules par evenements
    sans creer de couplage direct.

    Returns:
        Instance de l'EventBus connecte au CoreEventBus.
    """
    return EventBusImpl(CoreEventBus)


def get_entity_info(db: Session = Depends(get_db)) -> EntityInfoService:
    """
    Retourne le service d'information des entites.

    Ce service permet de recuperer les infos utilisateur/chantier
    SANS importer directement les modules auth/chantiers.

    Args:
        db: Session SQLAlchemy.

    Returns:
        Instance du service.
    """
    return get_entity_info_service(db)


def get_affectation_presenter(
    entity_info: EntityInfoService = Depends(get_entity_info),
) -> AffectationPresenter:
    """
    Retourne le presenter pour enrichir les affectations.

    Le presenter ajoute les infos d'affichage (nom, couleur)
    aux DTOs d'affectation.

    Args:
        entity_info: Service d'information des entites.

    Returns:
        Instance du presenter.
    """
    return AffectationPresenter(entity_info)


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


def _wrap_user_info(entity_info: EntityInfoService):
    """Wrap EntityInfoService.get_user_info pour retourner un dict."""
    def get_user_info(user_id: int):
        info = entity_info.get_user_info(user_id)
        if info:
            return {"nom": info.nom, "couleur": info.couleur, "metier": info.metier}
        return {}
    return get_user_info


def _wrap_chantier_info(entity_info: EntityInfoService):
    """Wrap EntityInfoService.get_chantier_info pour retourner un dict."""
    def get_chantier_info(chantier_id: int):
        info = entity_info.get_chantier_info(chantier_id)
        if info:
            return {"nom": info.nom, "couleur": info.couleur}
        return {}
    return get_chantier_info


def get_get_planning_use_case(
    affectation_repo: SQLAlchemyAffectationRepository = Depends(get_affectation_repository),
    entity_info: EntityInfoService = Depends(get_entity_info),
) -> GetPlanningUseCase:
    """
    Retourne le use case de recuperation du planning.

    Note: L'enrichissement reste dans le Use Case car le filtre
    par metier necessite cette information. C'est un compromis
    documente pour eviter une refactorisation majeure.
    Les infos sont recuperees via le service shared EntityInfoService.
    """
    return GetPlanningUseCase(
        affectation_repo=affectation_repo,
        get_user_info=_wrap_user_info(entity_info),
        get_chantier_info=_wrap_chantier_info(entity_info),
        get_user_chantiers=entity_info.get_user_chantier_ids,
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
    entity_info: EntityInfoService = Depends(get_entity_info),
) -> GetNonPlanifiesUseCase:
    """Retourne le use case de recuperation des non planifies."""
    return GetNonPlanifiesUseCase(
        affectation_repo=affectation_repo,
        get_active_user_ids=entity_info.get_active_user_ids,
    )


def get_planning_controller(
    create_uc: CreateAffectationUseCase = Depends(get_create_affectation_use_case),
    update_uc: UpdateAffectationUseCase = Depends(get_update_affectation_use_case),
    delete_uc: DeleteAffectationUseCase = Depends(get_delete_affectation_use_case),
    get_planning_uc: GetPlanningUseCase = Depends(get_get_planning_use_case),
    duplicate_uc: DuplicateAffectationsUseCase = Depends(get_duplicate_affectations_use_case),
    get_non_planifies_uc: GetNonPlanifiesUseCase = Depends(get_get_non_planifies_use_case),
    presenter: AffectationPresenter = Depends(get_affectation_presenter),
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
        presenter: Presenter pour enrichir les reponses.

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
        presenter=presenter,
    )
