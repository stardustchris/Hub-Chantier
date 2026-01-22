"""Value Object TypeRecurrence - Représente le type de récurrence d'une affectation."""

from enum import Enum
from typing import List


class TypeRecurrence(Enum):
    """
    Enumération des types de récurrence pour une affectation.

    Selon CDC Section 5.4 - Structure d'une affectation.
    Recurrence: Unique / Répéter (jours sélectionnés).

    Attributes:
        UNIQUE: Affectation ponctuelle, une seule fois.
        QUOTIDIEN: Répétition tous les jours ouvrés.
        HEBDOMADAIRE: Répétition chaque semaine aux mêmes jours.
    """

    UNIQUE = "unique"
    QUOTIDIEN = "quotidien"
    HEBDOMADAIRE = "hebdomadaire"

    @classmethod
    def from_string(cls, value: str) -> "TypeRecurrence":
        """
        Crée un TypeRecurrence depuis une chaîne.

        Args:
            value: La valeur en chaîne.

        Returns:
            Le TypeRecurrence correspondant.

        Raises:
            ValueError: Si la valeur n'est pas valide.
        """
        value_lower = value.lower()
        for member in cls:
            if member.value == value_lower:
                return member
        valid_values = [m.value for m in cls]
        raise ValueError(
            f"Type de récurrence invalide: {value}. "
            f"Valeurs acceptées: {valid_values}"
        )

    @classmethod
    def values(cls) -> List[str]:
        """Retourne la liste des valeurs valides."""
        return [member.value for member in cls]

    def __str__(self) -> str:
        """Retourne la valeur de l'enum."""
        return self.value
