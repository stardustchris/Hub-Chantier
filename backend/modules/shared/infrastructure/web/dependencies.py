"""Dépendances FastAPI pour le module Audit."""

from fastapi import Depends
from sqlalchemy.orm import Session

from shared.infrastructure.database import get_db
from ...application.services.audit_service import AuditService
from ...infrastructure.persistence.sqlalchemy_audit_repository import SQLAlchemyAuditRepository


def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    """
    Factory pour créer une instance du service d'audit.

    Cette fonction est utilisée par FastAPI pour l'injection de dépendances.
    Elle crée les instances nécessaires (repository, service) avec la session DB.

    Args:
        db: Session SQLAlchemy injectée par FastAPI.

    Returns:
        Instance du service AuditService configurée.

    Example:
        >>> @router.get("/audit/history/{entity_type}/{entity_id}")
        >>> def get_history(
        ...     entity_type: str,
        ...     entity_id: str,
        ...     service: AuditService = Depends(get_audit_service),
        ... ):
        ...     return service.get_history(entity_type, entity_id)
    """
    repository = SQLAlchemyAuditRepository(db)
    return AuditService(repository)
