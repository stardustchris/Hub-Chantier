"""Value Object TypeVariablePaie - Types de variables de paie."""

from enum import Enum


class TypeVariablePaie(Enum):
    """
    Types de variables de paie.

    Selon CDC Section 7.3 - Variables de Paie (FDH-13).
    """

    # Heures
    HEURES_NORMALES = "heures_normales"
    HEURES_SUPPLEMENTAIRES = "heures_supplementaires"
    HEURES_NUIT = "heures_nuit"
    HEURES_DIMANCHE = "heures_dimanche"
    HEURES_FERIE = "heures_ferie"

    # Indemnités
    PANIER_REPAS = "panier_repas"
    INDEMNITE_TRANSPORT = "indemnite_transport"
    PRIME_INTEMPERIES = "prime_intemperies"
    PRIME_SALISSURE = "prime_salissure"
    PRIME_OUTILLAGE = "prime_outillage"

    # Absences
    CONGES_PAYES = "conges_payes"
    RTT = "rtt"
    MALADIE = "maladie"
    ACCIDENT_TRAVAIL = "accident_travail"
    ABSENCE_INJUSTIFIEE = "absence_injustifiee"
    ABSENCE_JUSTIFIEE = "absence_justifiee"

    # Autres
    FORMATION = "formation"
    DEPLACEMENT = "deplacement"

    @classmethod
    def from_string(cls, value: str) -> "TypeVariablePaie":
        """
        Convertit une chaîne en TypeVariablePaie.

        Args:
            value: La valeur string.

        Returns:
            Le TypeVariablePaie correspondant.

        Raises:
            ValueError: Si la valeur n'est pas valide.
        """
        try:
            return cls(value.lower())
        except ValueError:
            valid_values = [t.value for t in cls]
            raise ValueError(f"Type invalide: {value}. Valeurs valides: {valid_values}")

    def is_hours_type(self) -> bool:
        """Vérifie si c'est un type d'heures."""
        return self in [
            TypeVariablePaie.HEURES_NORMALES,
            TypeVariablePaie.HEURES_SUPPLEMENTAIRES,
            TypeVariablePaie.HEURES_NUIT,
            TypeVariablePaie.HEURES_DIMANCHE,
            TypeVariablePaie.HEURES_FERIE,
        ]

    def is_allowance_type(self) -> bool:
        """Vérifie si c'est une indemnité."""
        return self in [
            TypeVariablePaie.PANIER_REPAS,
            TypeVariablePaie.INDEMNITE_TRANSPORT,
            TypeVariablePaie.PRIME_INTEMPERIES,
            TypeVariablePaie.PRIME_SALISSURE,
            TypeVariablePaie.PRIME_OUTILLAGE,
        ]

    def is_absence_type(self) -> bool:
        """Vérifie si c'est une absence."""
        return self in [
            TypeVariablePaie.CONGES_PAYES,
            TypeVariablePaie.RTT,
            TypeVariablePaie.MALADIE,
            TypeVariablePaie.ACCIDENT_TRAVAIL,
            TypeVariablePaie.ABSENCE_INJUSTIFIEE,
            TypeVariablePaie.ABSENCE_JUSTIFIEE,
        ]

    @property
    def libelle(self) -> str:
        """Retourne le libellé français."""
        libelles = {
            TypeVariablePaie.HEURES_NORMALES: "Heures normales",
            TypeVariablePaie.HEURES_SUPPLEMENTAIRES: "Heures supplémentaires",
            TypeVariablePaie.HEURES_NUIT: "Heures de nuit",
            TypeVariablePaie.HEURES_DIMANCHE: "Heures dimanche",
            TypeVariablePaie.HEURES_FERIE: "Heures jour férié",
            TypeVariablePaie.PANIER_REPAS: "Panier repas",
            TypeVariablePaie.INDEMNITE_TRANSPORT: "Indemnité transport",
            TypeVariablePaie.PRIME_INTEMPERIES: "Prime intempéries",
            TypeVariablePaie.PRIME_SALISSURE: "Prime salissure",
            TypeVariablePaie.PRIME_OUTILLAGE: "Prime outillage",
            TypeVariablePaie.CONGES_PAYES: "Congés payés",
            TypeVariablePaie.RTT: "RTT",
            TypeVariablePaie.MALADIE: "Maladie",
            TypeVariablePaie.ACCIDENT_TRAVAIL: "Accident du travail",
            TypeVariablePaie.ABSENCE_INJUSTIFIEE: "Absence injustifiée",
            TypeVariablePaie.ABSENCE_JUSTIFIEE: "Absence justifiée",
            TypeVariablePaie.FORMATION: "Formation",
            TypeVariablePaie.DEPLACEMENT: "Déplacement",
        }
        return libelles.get(self, self.value)
