"""Value Object TypeChamp - Types de champs disponibles dans les formulaires."""

from enum import Enum


class TypeChamp(str, Enum):
    """
    Types de champs disponibles dans les formulaires.

    Selon CDC Section 8 - Formulaires Chantier.
    Supporte FOR-03 (champs auto-remplis), FOR-04 (photos), FOR-05 (signature).
    """

    # Champs texte
    TEXTE = "texte"
    TEXTE_LONG = "texte_long"
    NOMBRE = "nombre"
    DATE = "date"
    HEURE = "heure"
    DATE_HEURE = "date_heure"

    # Champs selection
    CHECKBOX = "checkbox"
    RADIO = "radio"
    SELECT = "select"
    MULTI_SELECT = "multi_select"

    # Champs auto-remplis (FOR-03)
    AUTO_DATE = "auto_date"
    AUTO_HEURE = "auto_heure"
    AUTO_LOCALISATION = "auto_localisation"
    AUTO_INTERVENANT = "auto_intervenant"

    # Champs media (FOR-04)
    PHOTO = "photo"
    PHOTO_MULTIPLE = "photo_multiple"

    # Champ signature (FOR-05)
    SIGNATURE = "signature"

    # Champs specifiques
    TITRE_SECTION = "titre_section"
    SEPARATEUR = "separateur"

    @property
    def est_auto_rempli(self) -> bool:
        """Verifie si le champ est auto-rempli."""
        return self in [
            TypeChamp.AUTO_DATE,
            TypeChamp.AUTO_HEURE,
            TypeChamp.AUTO_LOCALISATION,
            TypeChamp.AUTO_INTERVENANT,
        ]

    @property
    def est_media(self) -> bool:
        """Verifie si le champ est de type media."""
        return self in [TypeChamp.PHOTO, TypeChamp.PHOTO_MULTIPLE]

    @property
    def est_signature(self) -> bool:
        """Verifie si le champ est une signature."""
        return self == TypeChamp.SIGNATURE

    @property
    def est_decoratif(self) -> bool:
        """Verifie si le champ est decoratif (non-saisissable)."""
        return self in [TypeChamp.TITRE_SECTION, TypeChamp.SEPARATEUR]

    @classmethod
    def from_string(cls, value: str) -> "TypeChamp":
        """Cree un TypeChamp depuis une chaine."""
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(f"Type de champ invalide: {value}")

    @classmethod
    def list_all(cls) -> list[str]:
        """Retourne la liste de tous les types de champs."""
        return [t.value for t in cls]
