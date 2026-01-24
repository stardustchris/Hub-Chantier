"""Value Object pour les plages horaires.

LOG-05, LOG-09: Gestion des créneaux horaires.
"""

from dataclasses import dataclass
from datetime import time
from typing import Optional


@dataclass(frozen=True)
class PlageHoraire:
    """Représente une plage horaire.

    LOG-05: Axe horaire vertical 08:00 → 18:00 (configurable)
    LOG-09: Sélection créneau - Date + heure début / heure fin
    """

    heure_debut: time
    heure_fin: time

    def __post_init__(self) -> None:
        """Valide que l'heure de fin est après l'heure de début."""
        if self.heure_fin <= self.heure_debut:
            raise ValueError(
                f"L'heure de fin ({self.heure_fin}) doit être après "
                f"l'heure de début ({self.heure_debut})"
            )

    @classmethod
    def par_defaut(cls) -> "PlageHoraire":
        """Retourne la plage horaire par défaut (08:00-18:00).

        LOG-05: Plage par défaut configurable.
        """
        return cls(heure_debut=time(8, 0), heure_fin=time(18, 0))

    @classmethod
    def from_strings(cls, debut: str, fin: str) -> "PlageHoraire":
        """Crée une plage horaire depuis des chaînes HH:MM.

        Args:
            debut: Heure de début au format HH:MM
            fin: Heure de fin au format HH:MM

        Returns:
            PlageHoraire validée
        """
        heure_debut = time.fromisoformat(debut)
        heure_fin = time.fromisoformat(fin)
        return cls(heure_debut=heure_debut, heure_fin=heure_fin)

    @property
    def duree_minutes(self) -> int:
        """Retourne la durée de la plage en minutes."""
        debut_minutes = self.heure_debut.hour * 60 + self.heure_debut.minute
        fin_minutes = self.heure_fin.hour * 60 + self.heure_fin.minute
        return fin_minutes - debut_minutes

    @property
    def duree_heures(self) -> float:
        """Retourne la durée de la plage en heures."""
        return self.duree_minutes / 60

    def chevauche(self, autre: "PlageHoraire") -> bool:
        """Vérifie si cette plage chevauche une autre plage.

        LOG-17: Conflit de réservation - Alerte si créneau déjà occupé.
        """
        return not (
            self.heure_fin <= autre.heure_debut or self.heure_debut >= autre.heure_fin
        )

    def contient(self, heure: time) -> bool:
        """Vérifie si une heure est contenue dans la plage."""
        return self.heure_debut <= heure < self.heure_fin

    def format_display(self) -> str:
        """Retourne un format d'affichage lisible."""
        return f"{self.heure_debut.strftime('%H:%M')} - {self.heure_fin.strftime('%H:%M')}"

    def to_dict(self) -> dict:
        """Convertit en dictionnaire pour sérialisation."""
        return {
            "heure_debut": self.heure_debut.isoformat(),
            "heure_fin": self.heure_fin.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> Optional["PlageHoraire"]:
        """Crée depuis un dictionnaire."""
        if not data:
            return None
        return cls.from_strings(data["heure_debut"], data["heure_fin"])
