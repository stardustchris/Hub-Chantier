"""Value Object pour le type de fournisseur.

FIN-14: Répertoire fournisseurs - Types de fournisseurs BTP.
"""

from enum import Enum


class TypeFournisseur(str, Enum):
    """Types de fournisseurs BTP.

    Catégories métier pour classifier les fournisseurs
    selon leur activité principale.
    """

    NEGOCE_MATERIAUX = "negoce_materiaux"
    LOUEUR = "loueur"
    SOUS_TRAITANT = "sous_traitant"
    SERVICE = "service"

    @property
    def label(self) -> str:
        """Retourne le libellé affichable du type."""
        labels = {
            self.NEGOCE_MATERIAUX: "Négoce matériaux",
            self.LOUEUR: "Loueur",
            self.SOUS_TRAITANT: "Sous-traitant",
            self.SERVICE: "Service",
        }
        return labels[self]
