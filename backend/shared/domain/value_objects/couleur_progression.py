"""Value Object CouleurProgression - Code couleur de progression.

Ce Value Object est partagé entre modules pour représenter l'avancement
d'une tâche ou d'une activité selon les heures réalisées vs estimées.
"""

from enum import Enum


class CouleurProgression(Enum):
    """
    Code couleur d'avancement d'une tâche/activité.

    Utilisé notamment pour TAC-20 (statistiques tâches) et exports PDF.

    Règles:
    - Gris: Heures réalisées = 0 (non commencé)
    - Vert: Heures réalisées <= 80% estimées (dans les temps)
    - Jaune: Heures réalisées entre 80% et 100% (attention, limite proche)
    - Rouge: Heures réalisées > estimées (dépassement, retard)
    """

    GRIS = "gris"      # Non commencé
    VERT = "vert"      # Dans les temps
    JAUNE = "jaune"    # Attention
    ROUGE = "rouge"    # Dépassement

    @classmethod
    def from_progression(
        cls, heures_realisees: float, heures_estimees: float
    ) -> "CouleurProgression":
        """
        Détermine la couleur en fonction de la progression.

        Args:
            heures_realisees: Heures effectivement passées.
            heures_estimees: Heures prévues pour la réalisation.

        Returns:
            La CouleurProgression correspondante.

        Example:
            >>> CouleurProgression.from_progression(4, 10)
            <CouleurProgression.VERT: 'vert'>
            >>> CouleurProgression.from_progression(12, 10)
            <CouleurProgression.ROUGE: 'rouge'>
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
        """Retourne le code hexadécimal de la couleur.

        Returns:
            Code couleur hexadécimal (ex: "#4CAF50").
        """
        mapping = {
            CouleurProgression.GRIS: "#9E9E9E",
            CouleurProgression.VERT: "#4CAF50",
            CouleurProgression.JAUNE: "#FFC107",
            CouleurProgression.ROUGE: "#F44336",
        }
        return mapping.get(self, "#9E9E9E")

    @property
    def display_name(self) -> str:
        """Retourne le nom d'affichage de la couleur.

        Returns:
            Nom en français (ex: "Dans les temps").
        """
        mapping = {
            CouleurProgression.GRIS: "Non commencé",
            CouleurProgression.VERT: "Dans les temps",
            CouleurProgression.JAUNE: "Attention",
            CouleurProgression.ROUGE: "Dépassement",
        }
        return mapping.get(self, self.value)

    @property
    def icon(self) -> str:
        """Retourne l'emoji correspondant.

        Returns:
            Emoji unicode (ex: "🟢").
        """
        mapping = {
            CouleurProgression.GRIS: "⚪",
            CouleurProgression.VERT: "🟢",
            CouleurProgression.JAUNE: "🟡",
            CouleurProgression.ROUGE: "🔴",
        }
        return mapping.get(self, "")
