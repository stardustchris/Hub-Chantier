"""Value Objects du module pointages (feuilles d'heures)."""

from .statut_pointage import StatutPointage
from .type_variable_paie import TypeVariablePaie
from .duree import Duree
from .periode_paie import PeriodePaie

# Import partagé
from shared.domain.value_objects import Couleur

__all__ = [
    "StatutPointage",
    "TypeVariablePaie",
    "Duree",
    "PeriodePaie",
    "Couleur",
]
