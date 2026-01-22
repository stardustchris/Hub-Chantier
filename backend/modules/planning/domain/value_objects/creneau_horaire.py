"""Value Object CreneauHoraire - Représente un créneau horaire."""

from dataclasses import dataclass
from datetime import time
from typing import Optional


@dataclass(frozen=True)
class CreneauHoraire:
    """
    Value Object représentant un créneau horaire.

    Selon CDC Section 5.4 - Structure d'une affectation.
    Les heures de début et fin sont optionnelles.

    Attributes:
        heure_debut: Heure de prise de poste (optionnel).
        heure_fin: Heure de fin de journée (optionnel).
    """

    heure_debut: Optional[time] = None
    heure_fin: Optional[time] = None

    def __post_init__(self) -> None:
        """Valide que l'heure de fin est après l'heure de début."""
        if self.heure_debut and self.heure_fin:
            if self.heure_fin <= self.heure_debut:
                raise ValueError(
                    "L'heure de fin doit être après l'heure de début"
                )

    @classmethod
    def journee_complete(cls) -> "CreneauHoraire":
        """Crée un créneau pour une journée complète (7h-17h)."""
        return cls(
            heure_debut=time(7, 0),
            heure_fin=time(17, 0),
        )

    @classmethod
    def demi_journee_matin(cls) -> "CreneauHoraire":
        """Crée un créneau pour une demi-journée matin."""
        return cls(
            heure_debut=time(7, 0),
            heure_fin=time(12, 0),
        )

    @classmethod
    def demi_journee_apres_midi(cls) -> "CreneauHoraire":
        """Crée un créneau pour une demi-journée après-midi."""
        return cls(
            heure_debut=time(13, 0),
            heure_fin=time(17, 0),
        )

    def duree_heures(self) -> Optional[float]:
        """
        Calcule la durée du créneau en heures.

        Returns:
            Durée en heures, ou None si les heures ne sont pas définies.
        """
        if not self.heure_debut or not self.heure_fin:
            return None

        debut_minutes = self.heure_debut.hour * 60 + self.heure_debut.minute
        fin_minutes = self.heure_fin.hour * 60 + self.heure_fin.minute
        return (fin_minutes - debut_minutes) / 60

    def __str__(self) -> str:
        """Retourne une représentation lisible du créneau."""
        if not self.heure_debut and not self.heure_fin:
            return "Journée"
        if self.heure_debut and self.heure_fin:
            return f"{self.heure_debut.strftime('%H:%M')} - {self.heure_fin.strftime('%H:%M')}"
        if self.heure_debut:
            return f"À partir de {self.heure_debut.strftime('%H:%M')}"
        return f"Jusqu'à {self.heure_fin.strftime('%H:%M')}"
