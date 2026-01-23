"""Value Object StatutFormulaire - Statuts d'un formulaire rempli."""

from enum import Enum


class StatutFormulaire(str, Enum):
    """
    Statuts possibles d'un formulaire rempli.

    Selon CDC Section 8 - Formulaires Chantier.
    """

    BROUILLON = "brouillon"      # En cours de saisie
    SOUMIS = "soumis"            # Soumis avec horodatage (FOR-07)
    VALIDE = "valide"            # Valide par un responsable
    ARCHIVE = "archive"          # Archive pour historique

    @property
    def est_modifiable(self) -> bool:
        """Verifie si le formulaire est modifiable."""
        return self == StatutFormulaire.BROUILLON

    @property
    def est_soumis(self) -> bool:
        """Verifie si le formulaire a ete soumis."""
        return self in [StatutFormulaire.SOUMIS, StatutFormulaire.VALIDE, StatutFormulaire.ARCHIVE]

    @classmethod
    def from_string(cls, value: str) -> "StatutFormulaire":
        """Cree un StatutFormulaire depuis une chaine."""
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(f"Statut de formulaire invalide: {value}")
