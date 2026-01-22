"""Persistence layer du module pointages."""

from .models import Base, PointageModel, FeuilleHeuresModel, VariablePaieModel
from .sqlalchemy_pointage_repository import SQLAlchemyPointageRepository
from .sqlalchemy_feuille_heures_repository import SQLAlchemyFeuilleHeuresRepository
from .sqlalchemy_variable_paie_repository import SQLAlchemyVariablePaieRepository

__all__ = [
    # Base
    "Base",
    # Models
    "PointageModel",
    "FeuilleHeuresModel",
    "VariablePaieModel",
    # Repositories
    "SQLAlchemyPointageRepository",
    "SQLAlchemyFeuilleHeuresRepository",
    "SQLAlchemyVariablePaieRepository",
]
