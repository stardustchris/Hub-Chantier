"""Dépendances FastAPI pour le module chantiers."""

import logging
from typing import Optional
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
    FermerChantierUseCase,
)
from ..persistence import SQLAlchemyChantierRepository
from shared.infrastructure.database import get_db
from shared.infrastructure.web.dependencies import (  # Facade centralisée
    get_user_repository,
)
from shared.application.ports.chantier_cloture_check_port import ChantierClotureCheckPort

logger = logging.getLogger(__name__)


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

    Note: Utilise le Service Registry pour éviter les imports directs cross-module
    et respecter le principe d'isolation des modules selon Clean Architecture.
    """
    # Injection cross-module via Service Registry (graceful degradation)
    from shared.infrastructure.service_registry import get_service

    formulaire_repo = get_service("formulaire_repository", db)
    signalement_repo = get_service("signalement_repository", db)
    pointage_repo = get_service("pointage_repository", db)

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


def get_cloture_check_port(
    db: Session = Depends(get_db),
) -> Optional[ChantierClotureCheckPort]:
    """Instancie le port de vérification des pré-requis de clôture.

    Utilise le Service Registry pour récupérer les repositories financiers
    sans import direct, avec graceful degradation si le module financier
    n'est pas disponible.

    Args:
        db: Session base de données.

    Returns:
        ChantierClotureCheckPort ou None si les dépendances sont indisponibles.
    """
    try:
        from modules.financier.infrastructure.persistence import (
            SQLAlchemyAchatRepository,
            SQLAlchemySituationRepository,
            SQLAlchemyAvenantRepository,
            SQLAlchemyBudgetRepository,
        )
        from shared.infrastructure.adapters import ChantierClotureCheckAdapter

        return ChantierClotureCheckAdapter(
            achat_repo=SQLAlchemyAchatRepository(db),
            situation_repo=SQLAlchemySituationRepository(db),
            avenant_repo=SQLAlchemyAvenantRepository(db),
            budget_repo=SQLAlchemyBudgetRepository(db),
        )
    except ImportError as e:
        logger.warning(
            "Module financier non disponible pour la vérification de clôture: %s", e
        )
        return None
    except Exception as e:
        logger.warning(
            "Erreur lors de l'initialisation du port de clôture: %s", e
        )
        return None


def get_fermer_chantier_use_case(
    controller: ChantierController = Depends(get_chantier_controller),
    cloture_check: Optional[ChantierClotureCheckPort] = Depends(get_cloture_check_port),
) -> FermerChantierUseCase:
    """Retourne le use case de fermeture de chantier."""
    return FermerChantierUseCase(
        controller=controller,
        cloture_check=cloture_check,
    )


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
