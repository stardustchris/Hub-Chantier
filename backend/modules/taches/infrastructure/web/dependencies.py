"""Dependencies FastAPI pour le module Taches."""

from fastapi import Depends
from sqlalchemy.orm import Session

from shared.infrastructure.database import get_db
from ...adapters.controllers import TacheController
from ..persistence import (
    SQLAlchemyTacheRepository,
    SQLAlchemyTemplateModeleRepository,
    SQLAlchemyFeuilleTacheRepository,
)


def get_tache_controller(db: Session = Depends(get_db)) -> TacheController:
    """
    Factory pour creer un TacheController avec ses dependances.

    Args:
        db: Session de base de donnees injectee.

    Returns:
        Instance de TacheController configuree.
    """
    tache_repo = SQLAlchemyTacheRepository(db)
    template_repo = SQLAlchemyTemplateModeleRepository(db)
    feuille_repo = SQLAlchemyFeuilleTacheRepository(db)

    return TacheController(
        tache_repo=tache_repo,
        template_repo=template_repo,
        feuille_repo=feuille_repo,
    )
