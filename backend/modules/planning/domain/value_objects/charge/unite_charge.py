"""Value Object UniteCharge - Unite pour l'affichage de la charge."""

from enum import Enum


class UniteCharge(Enum):
    """
    Unite d'affichage de la charge de travail.

    Selon CDC PDC-05: Toggle Hrs / J/H (Basculer entre Heures et Jours/Homme).
    """

    HEURES = "heures"
    JOURS_HOMME = "jours_homme"

    @property
    def label(self) -> str:
        """Retourne le label court."""
        labels = {
            "heures": "Hrs",
            "jours_homme": "J/H",
        }
        return labels.get(self.value, self.value)

    @property
    def label_long(self) -> str:
        """Retourne le label complet."""
        labels = {
            "heures": "Heures",
            "jours_homme": "Jours/Homme",
        }
        return labels.get(self.value, self.value)

    def convertir(self, heures: float, heures_par_jour: float = 7.0) -> float:
        """
        Convertit des heures dans l'unite.

        Args:
            heures: Nombre d'heures.
            heures_par_jour: Heures de travail par jour (defaut: 7h).

        Returns:
            La valeur dans l'unite.
        """
        if self == UniteCharge.HEURES:
            return heures
        else:  # JOURS_HOMME
            return heures / heures_par_jour if heures_par_jour > 0 else 0.0

    def formater(self, valeur: float) -> str:
        """
        Formate une valeur avec l'unite.

        Args:
            valeur: La valeur a formater.

        Returns:
            La valeur formatee avec unite.
        """
        if self == UniteCharge.HEURES:
            return f"{valeur:.1f}h"
        else:  # JOURS_HOMME
            return f"{valeur:.1f} J/H"

    @classmethod
    def from_string(cls, value: str) -> "UniteCharge":
        """
        Cree une UniteCharge a partir d'une chaine.

        Args:
            value: La valeur (heures, hrs, jours_homme, j/h).

        Returns:
            L'UniteCharge correspondante.
        """
        value_lower = value.lower().replace("/", "_").replace(" ", "_")
        if value_lower in ("heures", "hrs", "h"):
            return cls.HEURES
        elif value_lower in ("jours_homme", "j_h", "jh", "journee", "journees"):
            return cls.JOURS_HOMME
        else:
            raise ValueError(f"Unite invalide: {value}. Valides: heures, jours_homme")
