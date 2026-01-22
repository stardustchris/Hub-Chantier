"""Dépendances FastAPI pour le module chantiers."""

from fastapi import Depends
from sqlalchemy.orm import Session

from ...adapters.controllers import ChantierController
from ...application.use_cases import (
    CreateChantierUseCase,
    GetChantierUseCase,
    ListChantiersUseCase,
    UpdateChantierUseCase,
    DeleteChantierUseCase,
    ChangeStatutUseCase,
    AssignResponsableUseCase,
)
from ..persistence import SQLAlchemyChantierRepository
from shared.infrastructure.database import get_db
from modules.auth.domain.repositories import UserRepository
from modules.auth.infrastructure.persistence import SQLAlchemyUserRepository


def get_chantier_repository(
    db: Session = Depends(get_db),
) -> SQLAlchemyChantierRepository:
    """Retourne le repository chantiers."""
    return SQLAlchemyChantierRepository(db)


def get_user_repository(
    db: Session = Depends(get_db),
) -> UserRepository:
    """Retourne le repository utilisateurs pour récupérer les infos des conducteurs/chefs."""
    return SQLAlchemyUserRepository(db)


def get_create_chantier_use_case(
    chantier_repo: SQLAlchemyChantierRepository = Depends(get_chantier_repository),
) -> CreateChantierUseCase:
    """Retourne le use case de création de chantier."""
    return CreateChantierUseCase(chantier_repo=chantier_repo)


def get_get_chantier_use_case(
    chantier_repo: SQLAlchemyChantierRepository = Depends(get_chantier_repository),
) -> GetChantierUseCase:
    """Retourne le use case de récupération de chantier."""
    return GetChantierUseCase(chantier_repo=chantier_repo)


def get_list_chantiers_use_case(
    chantier_repo: SQLAlchemyChantierRepository = Depends(get_chantier_repository),
) -> ListChantiersUseCase:
    """Retourne le use case de liste des chantiers."""
    return ListChantiersUseCase(chantier_repo=chantier_repo)


def get_update_chantier_use_case(
    chantier_repo: SQLAlchemyChantierRepository = Depends(get_chantier_repository),
) -> UpdateChantierUseCase:
    """Retourne le use case de mise à jour de chantier."""
    return UpdateChantierUseCase(chantier_repo=chantier_repo)


def get_delete_chantier_use_case(
    chantier_repo: SQLAlchemyChantierRepository = Depends(get_chantier_repository),
) -> DeleteChantierUseCase:
    """Retourne le use case de suppression de chantier."""
    return DeleteChantierUseCase(chantier_repo=chantier_repo)


def get_change_statut_use_case(
    chantier_repo: SQLAlchemyChantierRepository = Depends(get_chantier_repository),
) -> ChangeStatutUseCase:
    """Retourne le use case de changement de statut."""
    return ChangeStatutUseCase(chantier_repo=chantier_repo)


def get_assign_responsable_use_case(
    chantier_repo: SQLAlchemyChantierRepository = Depends(get_chantier_repository),
) -> AssignResponsableUseCase:
    """Retourne le use case d'assignation de responsable."""
    return AssignResponsableUseCase(chantier_repo=chantier_repo)


def get_chantier_controller(
    create_use_case: CreateChantierUseCase = Depends(get_create_chantier_use_case),
    get_use_case: GetChantierUseCase = Depends(get_get_chantier_use_case),
    list_use_case: ListChantiersUseCase = Depends(get_list_chantiers_use_case),
    update_use_case: UpdateChantierUseCase = Depends(get_update_chantier_use_case),
    delete_use_case: DeleteChantierUseCase = Depends(get_delete_chantier_use_case),
    change_statut_use_case: ChangeStatutUseCase = Depends(get_change_statut_use_case),
    assign_responsable_use_case: AssignResponsableUseCase = Depends(
        get_assign_responsable_use_case
    ),
) -> ChantierController:
    """Retourne le controller des chantiers."""
    return ChantierController(
        create_use_case=create_use_case,
        get_use_case=get_use_case,
        list_use_case=list_use_case,
        update_use_case=update_use_case,
        delete_use_case=delete_use_case,
        change_statut_use_case=change_statut_use_case,
        assign_responsable_use_case=assign_responsable_use_case,
    )
