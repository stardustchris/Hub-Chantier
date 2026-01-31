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
from shared.infrastructure.web.dependencies import (  # Facade centralisée
    get_user_repository,
)


def get_chantier_repository(
    db: Session = Depends(get_db),
) -> SQLAlchemyChantierRepository:
    """Retourne le repository chantiers."""
    return SQLAlchemyChantierRepository(db)


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
    db: Session = Depends(get_db),
) -> ChangeStatutUseCase:
    """Retourne le use case de changement de statut avec dépendances cross-module.

    Gap: GAP-CHT-001 - Injection repositories pour validation prérequis
    Gap: GAP-CHT-005 - Injection AuditService pour traçabilité
    """
    import logging
    logger = logging.getLogger(__name__)

    # Injection cross-module (optionnelle, graceful degradation)
    formulaire_repo = None
    signalement_repo = None
    pointage_repo = None

    try:
        from modules.formulaires.infrastructure.persistence import (
            SQLAlchemyFormulaireRempliRepository
        )
        formulaire_repo = SQLAlchemyFormulaireRempliRepository(db)
    except ImportError:
        logger.warning("FormulaireRempliRepository not available")

    try:
        from modules.signalements.infrastructure.persistence import (
            SQLAlchemySignalementRepository
        )
        signalement_repo = SQLAlchemySignalementRepository(db)
    except ImportError:
        logger.warning("SignalementRepository not available")

    try:
        from modules.pointages.infrastructure.persistence import (
            SQLAlchemyPointageRepository
        )
        pointage_repo = SQLAlchemyPointageRepository(db)
    except ImportError:
        logger.warning("PointageRepository not available")

    # Injection AuditService (GAP-CHT-005)
    from shared.infrastructure.audit import AuditService
    audit_service = AuditService(db)

    return ChangeStatutUseCase(
        chantier_repo,
        formulaire_repo,
        signalement_repo,
        pointage_repo,
        audit_service
    )


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
