"""Value Object pour le type de frais de chantier.

DEV-25: Frais de chantier - Compte prorata, frais generaux, installations.
"""

from enum import Enum


class TypeFraisChantier(str, Enum):
    """Types de frais de chantier applicables a un devis.

    Les frais de chantier sont des couts supplementaires qui s'ajoutent
    aux lots du devis. Ils peuvent etre repartis globalement ou au prorata
    des montants des lots.

    Values:
        COMPTE_PRORATA: Compte prorata inter-entreprises (partage des charges communes).
        FRAIS_GENERAUX: Frais generaux de chantier (encadrement, assurances, etc.).
        INSTALLATION_CHANTIER: Installations de chantier (base vie, clotures, etc.).
        AUTRE: Autre type de frais de chantier.
    """

    COMPTE_PRORATA = "compte_prorata"
    FRAIS_GENERAUX = "frais_generaux"
    INSTALLATION_CHANTIER = "installation_chantier"
    AUTRE = "autre"

    @property
    def label(self) -> str:
        """Retourne le libelle affichable du type de frais."""
        labels = {
            self.COMPTE_PRORATA: "Compte prorata",
            self.FRAIS_GENERAUX: "Frais generaux",
            self.INSTALLATION_CHANTIER: "Installation de chantier",
            self.AUTRE: "Autre",
        }
        return labels[self]
