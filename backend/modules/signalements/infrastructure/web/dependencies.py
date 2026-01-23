"""Dependencies FastAPI pour le module Signalements."""

from typing import Optional
from fastapi import Depends
from sqlalchemy.orm import Session

from shared.infrastructure.database import get_db
from modules.auth.infrastructure.web.dependencies import (
    get_current_user_id,
    get_current_user_role,
)
from ...adapters.controllers import SignalementController
from ..persistence import SQLAlchemySignalementRepository, SQLAlchemyReponseRepository


def get_current_user(
    user_id: int = Depends(get_current_user_id),
    user_role: str = Depends(get_current_user_role),
) -> dict:
    """
    Récupère les informations de l'utilisateur courant.

    Args:
        user_id: ID de l'utilisateur.
        user_role: Rôle de l'utilisateur.

    Returns:
        Dict avec id et role.
    """
    return {"id": user_id, "role": user_role}


def get_user_name_resolver(db: Session):
    """
    Crée une fonction pour résoudre les noms d'utilisateurs.

    Args:
        db: Session SQLAlchemy.

    Returns:
        Fonction qui prend un user_id et retourne le nom.
    """
    from modules.auth.infrastructure.persistence import UserModel

    def resolver(user_id: int) -> Optional[str]:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if user:
            return f"{user.prenom} {user.nom}" if hasattr(user, 'prenom') else user.nom
        return None

    return resolver


def get_signalement_controller(
    db: Session = Depends(get_db),
) -> SignalementController:
    """
    Crée une instance du controller Signalement.

    Args:
        db: Session SQLAlchemy.

    Returns:
        Instance du SignalementController.
    """
    signalement_repo = SQLAlchemySignalementRepository(db)
    reponse_repo = SQLAlchemyReponseRepository(db)
    user_name_resolver = get_user_name_resolver(db)

    return SignalementController(
        signalement_repository=signalement_repo,
        reponse_repository=reponse_repo,
        get_user_name=user_name_resolver,
    )
