"""DTOs pour l'evolution financiere temporelle (FIN-17).

Fournit les structures de donnees pour l'endpoint d'evolution financiere
mensuelle, destine a alimenter un graphique Recharts en frontend.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class EvolutionMensuelleDTO:
    """Point de donnee mensuel pour le graphique d'evolution.

    Attributes:
        mois: Le mois au format "MM/YYYY".
        prevu_cumule: Montant prevu cumule (Decimal serialise en str).
        engage_cumule: Montant engage cumule (Decimal serialise en str).
        realise_cumule: Montant realise cumule (Decimal serialise en str).
    """

    mois: str  # Format "MM/YYYY"
    prevu_cumule: str  # Decimal -> str
    engage_cumule: str
    realise_cumule: str

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire serialisable.

        Returns:
            Dictionnaire contenant les donnees du point mensuel.
        """
        return {
            "mois": self.mois,
            "prevu_cumule": self.prevu_cumule,
            "engage_cumule": self.engage_cumule,
            "realise_cumule": self.realise_cumule,
        }


@dataclass
class EvolutionFinanciereDTO:
    """Reponse complete de l'evolution financiere.

    Attributes:
        chantier_id: L'ID du chantier.
        points: Liste des points de donnees mensuels.
    """

    chantier_id: int
    points: List[EvolutionMensuelleDTO]

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire serialisable.

        Returns:
            Dictionnaire contenant l'evolution financiere complete.
        """
        return {
            "chantier_id": self.chantier_id,
            "points": [p.to_dict() for p in self.points],
        }
