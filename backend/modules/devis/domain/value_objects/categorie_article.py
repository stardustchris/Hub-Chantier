"""Value Object pour la categorie d'article.

DEV-01: Bibliotheque d'articles - Categories pour organiser les articles.
"""

from enum import Enum


class CategorieArticle(str, Enum):
    """Categories d'articles de la bibliotheque de prix.

    Permet d'organiser les articles par type d'ouvrage
    ou par corps de metier.
    """

    GROS_OEUVRE = "gros_oeuvre"
    SECOND_OEUVRE = "second_oeuvre"
    ELECTRICITE = "electricite"
    PLOMBERIE = "plomberie"
    CHAUFFAGE_CLIM = "chauffage_clim"
    MENUISERIE = "menuiserie"
    PEINTURE = "peinture"
    COUVERTURE = "couverture"
    TERRASSEMENT = "terrassement"
    VRD = "vrd"
    CHARPENTE = "charpente"
    ISOLATION = "isolation"
    CARRELAGE = "carrelage"
    MAIN_OEUVRE = "main_oeuvre"
    MATERIEL = "materiel"
    DIVERS = "divers"

    @property
    def label(self) -> str:
        """Retourne le libelle affichable de la categorie."""
        labels = {
            self.GROS_OEUVRE: "Gros oeuvre",
            self.SECOND_OEUVRE: "Second oeuvre",
            self.ELECTRICITE: "Electricite",
            self.PLOMBERIE: "Plomberie",
            self.CHAUFFAGE_CLIM: "Chauffage / Climatisation",
            self.MENUISERIE: "Menuiserie",
            self.PEINTURE: "Peinture",
            self.COUVERTURE: "Couverture",
            self.TERRASSEMENT: "Terrassement",
            self.VRD: "Voirie et Reseaux Divers",
            self.CHARPENTE: "Charpente",
            self.ISOLATION: "Isolation",
            self.CARRELAGE: "Carrelage",
            self.MAIN_OEUVRE: "Main d'oeuvre",
            self.MATERIEL: "Materiel",
            self.DIVERS: "Divers",
        }
        return labels[self]
