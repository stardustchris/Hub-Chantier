"""Value Object CategorieFormulaire - Categories de formulaires."""

from enum import Enum


class CategorieFormulaire(str, Enum):
    """
    Categories de formulaires disponibles.

    Selon CDC Section 8.3 - Types de formulaires.
    """

    INTERVENTION = "intervention"      # Rapport d'intervention, Bon de SAV
    RECEPTION = "reception"            # PV de reception, Constat de reserves
    SECURITE = "securite"              # Formulaire securite, Visite PPSPS
    INCIDENT = "incident"              # Declaration sinistre, Fiche non-conformite
    APPROVISIONNEMENT = "approvisionnement"  # Commande materiel, Bon de livraison
    ADMINISTRATIF = "administratif"    # Demande de conges, CERFA
    GROS_OEUVRE = "gros_oeuvre"       # Rapport journalier, Bon de betonnage
    AUTRE = "autre"

    @property
    def label(self) -> str:
        """Retourne le libelle de la categorie."""
        labels = {
            CategorieFormulaire.INTERVENTION: "Interventions",
            CategorieFormulaire.RECEPTION: "Reception",
            CategorieFormulaire.SECURITE: "Securite",
            CategorieFormulaire.INCIDENT: "Incidents",
            CategorieFormulaire.APPROVISIONNEMENT: "Approvisionnement",
            CategorieFormulaire.ADMINISTRATIF: "Administratif",
            CategorieFormulaire.GROS_OEUVRE: "Gros Oeuvre",
            CategorieFormulaire.AUTRE: "Autre",
        }
        return labels.get(self, self.value)

    @classmethod
    def from_string(cls, value: str) -> "CategorieFormulaire":
        """Cree une CategorieFormulaire depuis une chaine."""
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(f"Categorie de formulaire invalide: {value}")

    @classmethod
    def list_all(cls) -> list[dict]:
        """Retourne la liste de toutes les categories avec leurs labels."""
        return [{"value": c.value, "label": c.label} for c in cls]
