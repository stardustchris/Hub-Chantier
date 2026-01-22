"""Value Objects du module pointages (feuilles d'heures)."""

from .statut_pointage import StatutPointage
from .type_variable_paie import TypeVariablePaie
from .duree import Duree

# Import partagé
from shared.domain.value_objects import Couleur

__all__ = [
    "StatutPointage",
    "TypeVariablePaie",
    "Duree",
    "Couleur",
]
