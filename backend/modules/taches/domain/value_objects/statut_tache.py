"""Value Object StatutTache - Statut d'une tache selon CDC TAC-13."""

from enum import Enum


class StatutTache(Enum):
    """
    Statut d'une tache.

    Selon CDC Section 13 - TAC-13:
    - A faire (A_FAIRE)
    - Termine (TERMINE)
    """

    A_FAIRE = "a_faire"
    TERMINE = "termine"

    @classmethod
    def from_string(cls, value: str) -> "StatutTache":
        """
        Cree un StatutTache depuis une chaine.

        Args:
            value: La valeur en chaine (ex: "a_faire", "termine").

        Returns:
            Le StatutTache correspondant.

        Raises:
            ValueError: Si la valeur n'est pas valide.
        """
        value_lower = value.lower().strip()
        for status in cls:
            if status.value == value_lower:
                return status
        raise ValueError(
            f"Statut invalide: {value}. Valeurs possibles: {[s.value for s in cls]}"
        )

    def __str__(self) -> str:
        """Retourne la valeur string du statut."""
        return self.value

    @property
    def display_name(self) -> str:
        """Retourne le nom d'affichage du statut."""
        mapping = {
            StatutTache.A_FAIRE: "A faire",
            StatutTache.TERMINE: "Termine",
        }
        return mapping.get(self, self.value)

    @property
    def icon(self) -> str:
        """Retourne l'icone du statut selon CDC TAC-13."""
        mapping = {
            StatutTache.A_FAIRE: "☐",
            StatutTache.TERMINE: "✅",
        }
        return mapping.get(self, "")
