"""Value Object pour l'avancement d'une tache (cross-module).

FIN-03: Suivi croise avancement physique vs financier.
Recoit les donnees du module taches via raw SQL (decouplage Clean Architecture).
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class AvancementTache:
    """Represente l'avancement d'une tache depuis le module taches.

    Ce value object est peuple via raw SQL pour maintenir le decouplage
    entre les modules financier et taches (Clean Architecture).

    Attributes:
        tache_id: ID de la tache.
        titre: Titre de la tache.
        statut: Statut de la tache (a_faire, en_cours, terminee, etc.).
        heures_estimees: Heures estimees pour la tache.
        heures_realisees: Heures realisees (pointages valides).
        quantite_estimee: Quantite estimee.
        quantite_realisee: Quantite realisee.
        progression_pct: Pourcentage de progression (0-100).
    """

    tache_id: int
    titre: str
    statut: str
    heures_estimees: Optional[Decimal]
    heures_realisees: Decimal
    quantite_estimee: Optional[Decimal]
    quantite_realisee: Decimal
    progression_pct: Decimal
