"""Value Object pour les unites d'articles.

DEV-01: Bibliotheque d'articles - Unites de mesure pour les articles BTP.
"""

from enum import Enum


class UniteArticle(str, Enum):
    """Unites de mesure courantes pour les articles BTP.

    Utilisees pour quantifier les articles de la bibliotheque
    et les lignes de devis.
    """

    M2 = "m2"
    M3 = "m3"
    ML = "ml"
    U = "u"
    KG = "kg"
    T = "t"
    HEURE = "heure"
    JOUR = "jour"
    FORFAIT = "forfait"
    L = "l"
    ENS = "ens"

    @property
    def label(self) -> str:
        """Retourne le libelle affichable de l'unite."""
        labels = {
            self.M2: "Metre carre",
            self.M3: "Metre cube",
            self.ML: "Metre lineaire",
            self.U: "Unite",
            self.KG: "Kilogramme",
            self.T: "Tonne",
            self.HEURE: "Heure",
            self.JOUR: "Jour",
            self.FORFAIT: "Forfait",
            self.L: "Litre",
            self.ENS: "Ensemble",
        }
        return labels[self]

    @property
    def symbole(self) -> str:
        """Retourne le symbole abrege de l'unite."""
        symboles = {
            self.M2: "m\u00b2",
            self.M3: "m\u00b3",
            self.ML: "ml",
            self.U: "u",
            self.KG: "kg",
            self.T: "t",
            self.HEURE: "h",
            self.JOUR: "j",
            self.FORFAIT: "fft",
            self.L: "L",
            self.ENS: "ens",
        }
        return symboles[self]
