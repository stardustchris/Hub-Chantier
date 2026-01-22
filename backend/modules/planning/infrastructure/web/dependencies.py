"""Dépendances FastAPI pour le module planning."""

from fastapi import Depends
from sqlalchemy.orm import Session

from ...application.use_cases import (
    CreateAffectationUseCase,
    GetAffectationUseCase,
    ListAffectationsUseCase,
    UpdateAffectationUseCase,
    DeleteAffectationUseCase,
    DeplacerAffectationUseCase,
    DupliquerAffectationsUseCase,
)
from ...domain.repositories import AffectationRepository
from ..persistence import SQLAlchemyAffectationRepository
from shared.infrastructure.database import get_db


def get_affectation_repository(
    db: Session = Depends(get_db),
) -> AffectationRepository:
    """Retourne le repository affectations."""
    return SQLAlchemyAffectationRepository(db)


def get_create_affectation_use_case(
    repo: AffectationRepository = Depends(get_affectation_repository),
) -> CreateAffectationUseCase:
    """Retourne le use case de création d'affectation."""
    return CreateAffectationUseCase(affectation_repo=repo)


def get_get_affectation_use_case(
    repo: AffectationRepository = Depends(get_affectation_repository),
) -> GetAffectationUseCase:
    """Retourne le use case de récupération d'affectation."""
    return GetAffectationUseCase(affectation_repo=repo)


def get_list_affectations_use_case(
    repo: AffectationRepository = Depends(get_affectation_repository),
) -> ListAffectationsUseCase:
    """Retourne le use case de liste des affectations."""
    return ListAffectationsUseCase(affectation_repo=repo)


def get_update_affectation_use_case(
    repo: AffectationRepository = Depends(get_affectation_repository),
) -> UpdateAffectationUseCase:
    """Retourne le use case de mise à jour d'affectation."""
    return UpdateAffectationUseCase(affectation_repo=repo)


def get_delete_affectation_use_case(
    repo: AffectationRepository = Depends(get_affectation_repository),
) -> DeleteAffectationUseCase:
    """Retourne le use case de suppression d'affectation."""
    return DeleteAffectationUseCase(affectation_repo=repo)


def get_deplacer_affectation_use_case(
    repo: AffectationRepository = Depends(get_affectation_repository),
) -> DeplacerAffectationUseCase:
    """Retourne le use case de déplacement d'affectation."""
    return DeplacerAffectationUseCase(affectation_repo=repo)


def get_dupliquer_affectations_use_case(
    repo: AffectationRepository = Depends(get_affectation_repository),
) -> DupliquerAffectationsUseCase:
    """Retourne le use case de duplication d'affectations."""
    return DupliquerAffectationsUseCase(affectation_repo=repo)
