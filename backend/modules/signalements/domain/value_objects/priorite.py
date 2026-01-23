"""Value Object Priorite - Niveaux de priorité des signalements (SIG-14)."""

from enum import Enum
from datetime import timedelta


class Priorite(Enum):
    """
    Niveaux de priorité des signalements.

    Selon CDC SIG-14: 4 niveaux avec délais de traitement associés.
    """

    CRITIQUE = "critique"  # 4 heures
    HAUTE = "haute"  # 24 heures
    MOYENNE = "moyenne"  # 48 heures
    BASSE = "basse"  # 72 heures

    @property
    def delai_traitement(self) -> timedelta:
        """Retourne le délai de traitement maximum."""
        delais = {
            Priorite.CRITIQUE: timedelta(hours=4),
            Priorite.HAUTE: timedelta(hours=24),
            Priorite.MOYENNE: timedelta(hours=48),
            Priorite.BASSE: timedelta(hours=72),
        }
        return delais[self]

    @property
    def delai_heures(self) -> int:
        """Retourne le délai en heures."""
        heures = {
            Priorite.CRITIQUE: 4,
            Priorite.HAUTE: 24,
            Priorite.MOYENNE: 48,
            Priorite.BASSE: 72,
        }
        return heures[self]

    @property
    def label(self) -> str:
        """Retourne le label d'affichage."""
        labels = {
            Priorite.CRITIQUE: "Critique (4h)",
            Priorite.HAUTE: "Haute (24h)",
            Priorite.MOYENNE: "Moyenne (48h)",
            Priorite.BASSE: "Basse (72h)",
        }
        return labels[self]

    @property
    def couleur(self) -> str:
        """Retourne la couleur associée."""
        couleurs = {
            Priorite.CRITIQUE: "red",
            Priorite.HAUTE: "orange",
            Priorite.MOYENNE: "yellow",
            Priorite.BASSE: "green",
        }
        return couleurs[self]

    @property
    def icone(self) -> str:
        """Retourne l'icône associée."""
        icones = {
            Priorite.CRITIQUE: "alert-triangle",
            Priorite.HAUTE: "alert-circle",
            Priorite.MOYENNE: "info",
            Priorite.BASSE: "check-circle",
        }
        return icones[self]

    @property
    def ordre(self) -> int:
        """Retourne l'ordre de tri (plus petit = plus prioritaire)."""
        ordres = {
            Priorite.CRITIQUE: 1,
            Priorite.HAUTE: 2,
            Priorite.MOYENNE: 3,
            Priorite.BASSE: 4,
        }
        return ordres[self]

    @classmethod
    def from_string(cls, value: str) -> "Priorite":
        """
        Convertit une chaîne en Priorite.

        Args:
            value: La valeur à convertir.

        Returns:
            La priorité correspondante.

        Raises:
            ValueError: Si la valeur n'est pas valide.
        """
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(
                f"Priorité invalide: {value}. "
                f"Valeurs acceptées: {', '.join(p.value for p in cls)}"
            )

    @classmethod
    def list_all(cls) -> list["Priorite"]:
        """Retourne toutes les priorités triées par ordre."""
        return sorted(cls, key=lambda p: p.ordre)
