"""Repository interfaces du module pointages."""

from .pointage_repository import PointageRepository
from .feuille_heures_repository import FeuilleHeuresRepository
from .variable_paie_repository import VariablePaieRepository
from .macro_paie_repository import MacroPaieRepository

__all__ = [
    "PointageRepository",
    "FeuilleHeuresRepository",
    "VariablePaieRepository",
    "MacroPaieRepository",
]
