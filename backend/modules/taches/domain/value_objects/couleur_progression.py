"""Value Object CouleurProgression - Code couleur selon CDC TAC-20."""

from enum import Enum


class CouleurProgression(Enum):
    """
    Code couleur d'avancement d'une tache.

    Selon CDC Section 13 - TAC-20:
    - Vert: Heures realisees <= 80% estimees (dans les temps)
    - Jaune: Heures realisees entre 80% et 100% (attention, limite proche)
    - Rouge: Heures realisees > estimees (depassement, retard)
    - Gris: Heures realisees = 0 (non commence)
    """

    GRIS = "gris"      # Non commence
    VERT = "vert"      # Dans les temps
    JAUNE = "jaune"    # Attention
    ROUGE = "rouge"    # Depassement

    @classmethod
    def from_progression(
        cls, heures_realisees: float, heures_estimees: float
    ) -> "CouleurProgression":
        """
        Determine la couleur en fonction de la progression.

        Args:
            heures_realisees: Heures effectivement passees.
            heures_estimees: Heures prevues pour la realisation.

        Returns:
            La CouleurProgression correspondante.
        """
        if heures_realisees == 0:
            return cls.GRIS

        if heures_estimees <= 0:
            return cls.ROUGE if heures_realisees > 0 else cls.GRIS

        ratio = heures_realisees / heures_estimees

        if ratio <= 0.8:
            return cls.VERT
        elif ratio <= 1.0:
            return cls.JAUNE
        else:
            return cls.ROUGE

    def __str__(self) -> str:
        """Retourne la valeur string de la couleur."""
        return self.value

    @property
    def hex_code(self) -> str:
        """Retourne le code hexadecimal de la couleur."""
        mapping = {
            CouleurProgression.GRIS: "#9E9E9E",
            CouleurProgression.VERT: "#4CAF50",
            CouleurProgression.JAUNE: "#FFC107",
            CouleurProgression.ROUGE: "#F44336",
        }
        return mapping.get(self, "#9E9E9E")

    @property
    def display_name(self) -> str:
        """Retourne le nom d'affichage de la couleur."""
        mapping = {
            CouleurProgression.GRIS: "Non commence",
            CouleurProgression.VERT: "Dans les temps",
            CouleurProgression.JAUNE: "Attention",
            CouleurProgression.ROUGE: "Depassement",
        }
        return mapping.get(self, self.value)

    @property
    def icon(self) -> str:
        """Retourne l'emoji correspondant."""
        mapping = {
            CouleurProgression.GRIS: "⚪",
            CouleurProgression.VERT: "🟢",
            CouleurProgression.JAUNE: "🟡",
            CouleurProgression.ROUGE: "🔴",
        }
        return mapping.get(self, "")
