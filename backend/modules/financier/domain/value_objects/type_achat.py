"""Value Object pour le type d'achat.

FIN-05, FIN-06: Saisie et suivi des achats par type.
"""

from enum import Enum


class TypeAchat(str, Enum):
    """Types d'achats possibles sur un chantier.

    Permet de catégoriser les achats pour le suivi
    budgétaire et la ventilation par poste.
    """

    MATERIAU = "materiau"
    MATERIEL = "materiel"
    SOUS_TRAITANCE = "sous_traitance"
    SERVICE = "service"
    MAIN_OEUVRE = "main_oeuvre"

    @property
    def label(self) -> str:
        """Retourne le libellé affichable du type."""
        labels = {
            self.MATERIAU: "Matériau",
            self.MATERIEL: "Matériel",
            self.SOUS_TRAITANCE: "Sous-traitance",
            self.SERVICE: "Service",
            self.MAIN_OEUVRE: "Main d'œuvre",
        }
        return labels[self]
