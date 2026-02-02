"""Value Object pour le type d'ecart dans un comparatif de devis.

DEV-08: Variantes et revisions - Types d'ecarts detectes lors de la comparaison.
"""

from enum import Enum


class TypeEcart(str, Enum):
    """Types d'ecart possibles entre deux versions de devis.

    - AJOUT: Ligne presente uniquement dans la version cible.
    - SUPPRESSION: Ligne presente uniquement dans la version source.
    - MODIFICATION: Ligne presente dans les deux versions avec des differences.
    - IDENTIQUE: Ligne identique dans les deux versions.
    """

    AJOUT = "ajout"
    SUPPRESSION = "suppression"
    MODIFICATION = "modification"
    IDENTIQUE = "identique"

    @property
    def label(self) -> str:
        """Retourne le libelle affichable du type d'ecart."""
        labels = {
            self.AJOUT: "Ajout",
            self.SUPPRESSION: "Suppression",
            self.MODIFICATION: "Modification",
            self.IDENTIQUE: "Identique",
        }
        return labels[self]
