"""Value Object pour le type de version d'un devis.

DEV-08: Variantes et revisions - Types de versions possibles.
"""

from enum import Enum


class TypeVersion(str, Enum):
    """Types de version d'un devis.

    - ORIGINALE: Devis original (premier cree).
    - REVISION: Nouvelle version du meme devis (corrige/mis a jour).
    - VARIANTE: Version alternative (economique/standard/premium).
    """

    ORIGINALE = "originale"
    REVISION = "revision"
    VARIANTE = "variante"

    @property
    def label(self) -> str:
        """Retourne le libelle affichable du type de version."""
        labels = {
            self.ORIGINALE: "Originale",
            self.REVISION: "Revision",
            self.VARIANTE: "Variante",
        }
        return labels[self]

    @property
    def est_copie(self) -> bool:
        """Indique si ce type de version est une copie d'un original."""
        return self in {self.REVISION, self.VARIANTE}
