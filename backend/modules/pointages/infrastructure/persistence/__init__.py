"""Persistence layer du module pointages."""

from .models import (
    Base,
    PointageModel,
    FeuilleHeuresModel,
    VariablePaieModel,
    MacroPaieModel,
    SynchronisationPaieModel,
    CorrespondancePaieExterneModel,
)
from .sqlalchemy_pointage_repository import SQLAlchemyPointageRepository
from .sqlalchemy_feuille_heures_repository import SQLAlchemyFeuilleHeuresRepository
from .sqlalchemy_variable_paie_repository import SQLAlchemyVariablePaieRepository
from .sqlalchemy_macro_paie_repository import SQLAlchemyMacroPaieRepository
from .sqlalchemy_synchronisation_paie_repository import (
    SQLAlchemySynchronisationPaieRepository,
    SQLAlchemyCorrespondanceExterneRepository,
)

__all__ = [
    # Base
    "Base",
    # Models
    "PointageModel",
    "FeuilleHeuresModel",
    "VariablePaieModel",
    "MacroPaieModel",
    "SynchronisationPaieModel",
    "CorrespondancePaieExterneModel",
    # Repositories
    "SQLAlchemyPointageRepository",
    "SQLAlchemyFeuilleHeuresRepository",
    "SQLAlchemyVariablePaieRepository",
    "SQLAlchemyMacroPaieRepository",
    "SQLAlchemySynchronisationPaieRepository",
    "SQLAlchemyCorrespondanceExterneRepository",
]
