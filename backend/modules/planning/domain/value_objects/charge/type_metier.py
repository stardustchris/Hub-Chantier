"""Value Object TypeMetier - Type de metier pour le planning de charge."""

from enum import Enum


# Badges couleurs selon CDC Section 5.3 (defini hors de l'Enum)
_COULEURS_METIERS = {
    "employe": "#2C3E50",  # Bleu fonce
    "sous_traitant": "#E74C3C",  # Rouge/Corail
    "charpentier": "#27AE60",  # Vert
    "couvreur": "#E67E22",  # Orange
    "electricien": "#EC407A",  # Magenta/Rose
    "macon": "#795548",  # Marron
    "coffreur": "#F1C40F",  # Jaune
    "ferrailleur": "#607D8B",  # Gris fonce
    "grutier": "#1ABC9C",  # Cyan
}

_LABELS_METIERS = {
    "employe": "Employe",
    "sous_traitant": "Sous-traitant",
    "charpentier": "Charpentier",
    "couvreur": "Couvreur",
    "electricien": "Electricien",
    "macon": "Macon",
    "coffreur": "Coffreur",
    "ferrailleur": "Ferrailleur",
    "grutier": "Grutier",
}


class TypeMetier(Enum):
    """
    Enumeration des types de metiers.

    Selon CDC Section 5.3 - Badges metiers (Groupement).
    Utilise pour categoriser les besoins en main d'oeuvre.
    """

    # Metiers generiques
    EMPLOYE = "employe"
    SOUS_TRAITANT = "sous_traitant"

    # Metiers specialises BTP
    CHARPENTIER = "charpentier"
    COUVREUR = "couvreur"
    ELECTRICIEN = "electricien"

    # Metiers Gros Oeuvre (Greg Constructions)
    MACON = "macon"
    COFFREUR = "coffreur"
    FERRAILLEUR = "ferrailleur"
    GRUTIER = "grutier"

    @property
    def couleur(self) -> str:
        """Retourne la couleur associee au metier."""
        return _COULEURS_METIERS.get(self.value, "#3498DB")

    @property
    def label(self) -> str:
        """Retourne le label lisible du metier."""
        return _LABELS_METIERS.get(self.value, self.value.title())

    @classmethod
    def from_string(cls, value: str) -> "TypeMetier":
        """
        Cree un TypeMetier a partir d'une chaine.

        Args:
            value: La valeur du type.

        Returns:
            Le TypeMetier correspondant.

        Raises:
            ValueError: Si le type n'existe pas.
        """
        value_lower = value.lower().replace("-", "_").replace(" ", "_")
        for member in cls:
            if member.value == value_lower:
                return member
        valid = [m.value for m in cls]
        raise ValueError(f"Type de metier invalide: {value}. Valides: {valid}")

    @classmethod
    def all_types(cls) -> list["TypeMetier"]:
        """Retourne tous les types de metiers."""
        return list(cls)
