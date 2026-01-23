"""Value Object DossierType - Types de dossiers prédéfinis (GED-02)."""

from enum import Enum


class DossierType(Enum):
    """
    Types de dossiers prédéfinis selon l'arborescence type.

    Selon CDC Section 9.4 - Arborescence type.
    """

    PLANS = "01_plans"
    ADMINISTRATIF = "02_administratif"
    SECURITE = "03_securite"
    QUALITE = "04_qualite"
    PHOTOS = "05_photos"
    COMPTES_RENDUS = "06_comptes_rendus"
    LIVRAISONS = "07_livraisons"
    CUSTOM = "custom"

    @property
    def numero(self) -> str:
        """Retourne le numéro du dossier (pour le tri)."""
        if self == DossierType.CUSTOM:
            return "99"
        return self.value.split("_")[0]

    @property
    def nom_affichage(self) -> str:
        """Retourne le nom d'affichage du dossier."""
        noms = {
            DossierType.PLANS: "Plans",
            DossierType.ADMINISTRATIF: "Documents administratifs",
            DossierType.SECURITE: "Sécurité",
            DossierType.QUALITE: "Qualité",
            DossierType.PHOTOS: "Photos",
            DossierType.COMPTES_RENDUS: "Comptes-rendus",
            DossierType.LIVRAISONS: "Livraisons",
            DossierType.CUSTOM: "Personnalisé",
        }
        return noms[self]

    @property
    def description(self) -> str:
        """Retourne la description du contenu type."""
        descriptions = {
            DossierType.PLANS: "Plans d'exécution, plans béton, réservations",
            DossierType.ADMINISTRATIF: "Marchés, avenants, OS, situations",
            DossierType.SECURITE: "PPSPS, plan de prévention, consignes",
            DossierType.QUALITE: "Fiches techniques, PV essais, autocontrôles",
            DossierType.PHOTOS: "Photos chantier par date/zone",
            DossierType.COMPTES_RENDUS: "CR réunions, CR chantier",
            DossierType.LIVRAISONS: "Bons de livraison, bordereaux",
            DossierType.CUSTOM: "Dossier personnalisé",
        }
        return descriptions[self]

    @property
    def niveau_acces_defaut(self) -> str:
        """Retourne le niveau d'accès par défaut recommandé."""
        niveaux = {
            DossierType.PLANS: "compagnon",
            DossierType.ADMINISTRATIF: "conducteur",
            DossierType.SECURITE: "compagnon",
            DossierType.QUALITE: "chef_chantier",
            DossierType.PHOTOS: "compagnon",
            DossierType.COMPTES_RENDUS: "chef_chantier",
            DossierType.LIVRAISONS: "chef_chantier",
            DossierType.CUSTOM: "chef_chantier",
        }
        return niveaux[self]

    @classmethod
    def from_string(cls, value: str) -> "DossierType":
        """
        Crée un DossierType depuis une chaîne.

        Args:
            value: La valeur en chaîne.

        Returns:
            L'enum correspondant.

        Raises:
            ValueError: Si la valeur n'est pas valide.
        """
        try:
            return cls(value.lower())
        except ValueError:
            # Essayer avec les noms d'affichage
            for dt in cls:
                if dt.nom_affichage.lower() == value.lower():
                    return dt
            return cls.CUSTOM

    @classmethod
    def list_all(cls) -> list[dict]:
        """Retourne tous les types de dossiers avec leurs métadonnées."""
        return [
            {
                "value": dt.value,
                "numero": dt.numero,
                "nom": dt.nom_affichage,
                "description": dt.description,
                "niveau_acces_defaut": dt.niveau_acces_defaut,
            }
            for dt in cls
            if dt != cls.CUSTOM
        ]
