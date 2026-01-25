"""Value Object StatutIntervention.

INT-05: Statuts intervention - A planifier / Planifiee / En cours / Terminee / Annulee
"""

from enum import Enum
from typing import List


class StatutIntervention(str, Enum):
    """Statuts possibles d'une intervention.

    Cycle de vie:
    A_PLANIFIER -> PLANIFIEE -> EN_COURS -> TERMINEE
                            |            |-> ANNULEE
                            |-> ANNULEE
    """

    A_PLANIFIER = "a_planifier"
    PLANIFIEE = "planifiee"
    EN_COURS = "en_cours"
    TERMINEE = "terminee"
    ANNULEE = "annulee"

    @property
    def label(self) -> str:
        """Retourne le libelle affichable du statut."""
        labels = {
            StatutIntervention.A_PLANIFIER: "A planifier",
            StatutIntervention.PLANIFIEE: "Planifiee",
            StatutIntervention.EN_COURS: "En cours",
            StatutIntervention.TERMINEE: "Terminee",
            StatutIntervention.ANNULEE: "Annulee",
        }
        return labels[self]

    @property
    def couleur(self) -> str:
        """Retourne la couleur associee au statut."""
        couleurs = {
            StatutIntervention.A_PLANIFIER: "#F59E0B",  # Orange/Jaune
            StatutIntervention.PLANIFIEE: "#3B82F6",  # Bleu
            StatutIntervention.EN_COURS: "#10B981",  # Vert
            StatutIntervention.TERMINEE: "#6B7280",  # Gris
            StatutIntervention.ANNULEE: "#EF4444",  # Rouge
        }
        return couleurs[self]

    @property
    def icone(self) -> str:
        """Retourne l'icone emoji associee au statut."""
        icones = {
            StatutIntervention.A_PLANIFIER: "📋",
            StatutIntervention.PLANIFIEE: "📅",
            StatutIntervention.EN_COURS: "🔧",
            StatutIntervention.TERMINEE: "✅",
            StatutIntervention.ANNULEE: "❌",
        }
        return icones[self]

    @property
    def est_active(self) -> bool:
        """Verifie si l'intervention est active (non terminee/annulee)."""
        return self in (
            StatutIntervention.A_PLANIFIER,
            StatutIntervention.PLANIFIEE,
            StatutIntervention.EN_COURS,
        )

    @property
    def est_modifiable(self) -> bool:
        """Verifie si l'intervention peut etre modifiee."""
        return self != StatutIntervention.ANNULEE

    def transitions_possibles(self) -> List["StatutIntervention"]:
        """Retourne la liste des statuts vers lesquels on peut transitionner."""
        transitions = {
            StatutIntervention.A_PLANIFIER: [
                StatutIntervention.PLANIFIEE,
                StatutIntervention.ANNULEE,
            ],
            StatutIntervention.PLANIFIEE: [
                StatutIntervention.EN_COURS,
                StatutIntervention.A_PLANIFIER,
                StatutIntervention.ANNULEE,
            ],
            StatutIntervention.EN_COURS: [
                StatutIntervention.TERMINEE,
                StatutIntervention.ANNULEE,
            ],
            StatutIntervention.TERMINEE: [],  # Statut final
            StatutIntervention.ANNULEE: [],  # Statut final
        }
        return transitions.get(self, [])

    def peut_transitionner_vers(self, cible: "StatutIntervention") -> bool:
        """Verifie si la transition vers le statut cible est autorisee."""
        return cible in self.transitions_possibles()
