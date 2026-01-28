"""Value Objects du module Taches."""

from .statut_tache import StatutTache
from .unite_mesure import UniteMesure
# CouleurProgression déplacé vers shared.domain (réutilisable entre modules)
from shared.domain import CouleurProgression

__all__ = ["StatutTache", "UniteMesure", "CouleurProgression"]
