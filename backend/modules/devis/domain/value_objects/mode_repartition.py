"""Value Object pour le mode de repartition des frais de chantier.

DEV-25: Frais de chantier - Repartition globale ou par lot.
"""

from enum import Enum


class ModeRepartition(str, Enum):
    """Modes de repartition des frais de chantier sur les lots.

    Determine comment un frais de chantier est reparti sur les lots du devis.

    Values:
        GLOBAL: Le frais s'applique globalement au devis (non ventile par lot).
        PRORATA_LOTS: Le frais est reparti au prorata du montant HT de chaque lot.
    """

    GLOBAL = "global"
    PRORATA_LOTS = "prorata_lots"

    @property
    def label(self) -> str:
        """Retourne le libelle affichable du mode de repartition."""
        labels = {
            self.GLOBAL: "Global",
            self.PRORATA_LOTS: "Prorata des lots",
        }
        return labels[self]
