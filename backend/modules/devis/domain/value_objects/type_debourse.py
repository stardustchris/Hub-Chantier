"""Value Object pour le type de debourse.

DEV-05: Detail debourses avances - Types de couts directs.
"""

from enum import Enum


class TypeDebourse(str, Enum):
    """Types de debourses (couts directs) en BTP.

    Composantes du debourse sec :
    - MOE : Main d'oeuvre (heures x taux horaire)
    - MATERIAUX : Materiaux et fournitures
    - MATERIEL : Location ou amortissement equipements
    - SOUS_TRAITANCE : Montant forfaitaire ou metre sous-traitant
    - DEPLACEMENT : Frais de deplacement des ressources
    """

    MOE = "moe"
    MATERIAUX = "materiaux"
    MATERIEL = "materiel"
    SOUS_TRAITANCE = "sous_traitance"
    DEPLACEMENT = "deplacement"

    @property
    def label(self) -> str:
        """Retourne le libelle affichable du type de debourse."""
        labels = {
            self.MOE: "Main d'oeuvre",
            self.MATERIAUX: "Materiaux",
            self.MATERIEL: "Materiel",
            self.SOUS_TRAITANCE: "Sous-traitance",
            self.DEPLACEMENT: "Deplacement",
        }
        return labels[self]

    @property
    def code_court(self) -> str:
        """Retourne le code court pour les rapports."""
        codes = {
            self.MOE: "MO",
            self.MATERIAUX: "MAT",
            self.MATERIEL: "MTL",
            self.SOUS_TRAITANCE: "ST",
            self.DEPLACEMENT: "DEP",
        }
        return codes[self]
