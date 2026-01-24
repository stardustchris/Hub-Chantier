"""Value Object pour le type de ressource.

CDC Section 11.3 - Types de ressources (Greg Constructions).
"""
from enum import Enum


class TypeRessource(str, Enum):
    """
    Types de ressources disponibles.

    Selon CDC Section 11.3:
    - Engins de levage: N+1 requis
    - Engins de terrassement: N+1 requis
    - Vehicules: Validation optionnelle
    - Gros outillage: Validation optionnelle
    - Equipements: N+1 requis
    """

    LEVAGE = "levage"
    """Engins de levage: Grue mobile, Manitou, Nacelle, Chariot elevateur."""

    TERRASSEMENT = "terrassement"
    """Engins de terrassement: Mini-pelle, Pelleteuse, Compacteur, Dumper."""

    VEHICULE = "vehicule"
    """Vehicules: Camion benne, Fourgon, Vehicule utilitaire."""

    OUTILLAGE = "outillage"
    """Gros outillage: Betonniere, Vibrateur, Pompe a beton."""

    EQUIPEMENT = "equipement"
    """Equipements: Echafaudage, Etais, Banches, Coffrages."""

    @property
    def validation_requise_par_defaut(self) -> bool:
        """
        Indique si ce type de ressource requiert une validation N+1 par defaut.

        Returns:
            True si validation N+1 requise, False sinon.
        """
        return self in (
            TypeRessource.LEVAGE,
            TypeRessource.TERRASSEMENT,
            TypeRessource.EQUIPEMENT,
        )

    @property
    def label(self) -> str:
        """
        Libelle affichable du type de ressource.

        Returns:
            Le libelle en francais.
        """
        labels = {
            TypeRessource.LEVAGE: "Engins de levage",
            TypeRessource.TERRASSEMENT: "Engins de terrassement",
            TypeRessource.VEHICULE: "Vehicules",
            TypeRessource.OUTILLAGE: "Gros outillage",
            TypeRessource.EQUIPEMENT: "Equipements",
        }
        return labels.get(self, self.value)

    @property
    def exemples(self) -> list[str]:
        """
        Exemples de ressources pour ce type.

        Returns:
            Liste d'exemples.
        """
        exemples = {
            TypeRessource.LEVAGE: ["Grue mobile", "Manitou", "Nacelle", "Chariot elevateur"],
            TypeRessource.TERRASSEMENT: ["Mini-pelle", "Pelleteuse", "Compacteur", "Dumper"],
            TypeRessource.VEHICULE: ["Camion benne", "Fourgon", "Vehicule utilitaire"],
            TypeRessource.OUTILLAGE: ["Betonniere", "Vibrateur", "Pompe a beton"],
            TypeRessource.EQUIPEMENT: ["Echafaudage", "Etais", "Banches", "Coffrages"],
        }
        return exemples.get(self, [])
