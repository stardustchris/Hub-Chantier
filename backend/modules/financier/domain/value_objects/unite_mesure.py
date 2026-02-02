"""Value Object pour les unités de mesure.

FIN-02, FIN-05: Unités utilisées pour les lots budgétaires et achats BTP.
"""

from enum import Enum


class UniteMesure(str, Enum):
    """Unités de mesure courantes en BTP.

    Utilisées pour quantifier les lots budgétaires
    et les lignes d'achat.
    """

    M2 = "m2"
    M3 = "m3"
    FORFAIT = "forfait"
    KG = "kg"
    HEURE = "heure"
    ML = "ml"
    T = "T"
    U = "u"

    @property
    def label(self) -> str:
        """Retourne le libellé affichable de l'unité."""
        labels = {
            self.M2: "Mètre carré",
            self.M3: "Mètre cube",
            self.FORFAIT: "Forfait",
            self.KG: "Kilogramme",
            self.HEURE: "Heure",
            self.ML: "Mètre linéaire",
            self.T: "Tonne",
            self.U: "Unité",
        }
        return labels[self]

    @property
    def symbole(self) -> str:
        """Retourne le symbole abrégé de l'unité."""
        symboles = {
            self.M2: "m²",
            self.M3: "m³",
            self.FORFAIT: "fft",
            self.KG: "kg",
            self.HEURE: "h",
            self.ML: "ml",
            self.T: "T",
            self.U: "u",
        }
        return symboles[self]
