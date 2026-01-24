"""Value Object pour la catégorie de ressource.

LOG-01, LOG-02: Types de ressources gérées par l'entreprise.
"""

from enum import Enum
from typing import List


class CategorieRessource(str, Enum):
    """Catégories de ressources matérielles.

    Selon le CDC Section 11.3:
    - Engins de levage: Grue mobile, Manitou, Nacelle, Chariot élévateur
    - Engins de terrassement: Mini-pelle, Pelleteuse, Compacteur, Dumper
    - Véhicules: Camion benne, Fourgon, Véhicule utilitaire
    - Gros outillage: Bétonnière, Vibrateur, Pompe à béton
    - Équipements: Échafaudage, Étais, Banches, Coffrages
    """

    ENGIN_LEVAGE = "engin_levage"
    ENGIN_TERRASSEMENT = "engin_terrassement"
    VEHICULE = "vehicule"
    GROS_OUTILLAGE = "gros_outillage"
    EQUIPEMENT = "equipement"

    @property
    def label(self) -> str:
        """Retourne le libellé affichable de la catégorie."""
        labels = {
            self.ENGIN_LEVAGE: "Engin de levage",
            self.ENGIN_TERRASSEMENT: "Engin de terrassement",
            self.VEHICULE: "Véhicule",
            self.GROS_OUTILLAGE: "Gros outillage",
            self.EQUIPEMENT: "Équipement",
        }
        return labels[self]

    @property
    def exemples(self) -> List[str]:
        """Retourne des exemples pour cette catégorie."""
        exemples = {
            self.ENGIN_LEVAGE: ["Grue mobile", "Manitou", "Nacelle", "Chariot élévateur"],
            self.ENGIN_TERRASSEMENT: ["Mini-pelle", "Pelleteuse", "Compacteur", "Dumper"],
            self.VEHICULE: ["Camion benne", "Fourgon", "Véhicule utilitaire"],
            self.GROS_OUTILLAGE: ["Bétonnière", "Vibrateur", "Pompe à béton"],
            self.EQUIPEMENT: ["Échafaudage", "Étais", "Banches", "Coffrages"],
        }
        return exemples[self]

    @property
    def validation_requise(self) -> bool:
        """Indique si la validation N+1 est requise par défaut.

        LOG-10: Option validation N+1 - Activation/désactivation par ressource.
        Certaines catégories requièrent une validation obligatoire.
        """
        categories_validation_requise = {
            self.ENGIN_LEVAGE,
            self.ENGIN_TERRASSEMENT,
            self.EQUIPEMENT,
        }
        return self in categories_validation_requise

    @classmethod
    def all_categories(cls) -> List["CategorieRessource"]:
        """Retourne toutes les catégories disponibles."""
        return list(cls)
