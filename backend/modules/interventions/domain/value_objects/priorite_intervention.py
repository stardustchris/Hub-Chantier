"""Value Object PrioriteIntervention.

INT-04: Fiche intervention - priorite
"""

from enum import Enum


class PrioriteIntervention(str, Enum):
    """Niveaux de priorite d'une intervention."""

    BASSE = "basse"
    NORMALE = "normale"
    HAUTE = "haute"
    URGENTE = "urgente"

    @property
    def label(self) -> str:
        """Retourne le libelle affichable de la priorite."""
        labels = {
            PrioriteIntervention.BASSE: "Basse",
            PrioriteIntervention.NORMALE: "Normale",
            PrioriteIntervention.HAUTE: "Haute",
            PrioriteIntervention.URGENTE: "Urgente",
        }
        return labels[self]

    @property
    def couleur(self) -> str:
        """Retourne la couleur associee a la priorite."""
        couleurs = {
            PrioriteIntervention.BASSE: "#6B7280",  # Gris
            PrioriteIntervention.NORMALE: "#3B82F6",  # Bleu
            PrioriteIntervention.HAUTE: "#F59E0B",  # Orange
            PrioriteIntervention.URGENTE: "#EF4444",  # Rouge
        }
        return couleurs[self]

    @property
    def icone(self) -> str:
        """Retourne l'icone associee a la priorite."""
        icones = {
            PrioriteIntervention.BASSE: "🔵",
            PrioriteIntervention.NORMALE: "🟢",
            PrioriteIntervention.HAUTE: "🟠",
            PrioriteIntervention.URGENTE: "🔴",
        }
        return icones[self]

    @property
    def ordre(self) -> int:
        """Retourne l'ordre de priorite (plus eleve = plus urgent)."""
        ordres = {
            PrioriteIntervention.BASSE: 1,
            PrioriteIntervention.NORMALE: 2,
            PrioriteIntervention.HAUTE: 3,
            PrioriteIntervention.URGENTE: 4,
        }
        return ordres[self]

    def __lt__(self, other: "PrioriteIntervention") -> bool:
        """Comparaison pour le tri."""
        return self.ordre < other.ordre

    def __le__(self, other: "PrioriteIntervention") -> bool:
        """Comparaison pour le tri."""
        return self.ordre <= other.ordre
