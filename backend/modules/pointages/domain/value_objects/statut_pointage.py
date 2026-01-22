"""Value Object StatutPointage - Statut de validation d'un pointage."""

from enum import Enum


class StatutPointage(Enum):
    """
    Statut de validation d'un pointage.

    Selon CDC Section 7 - Feuilles d'heures (FDH-12 Signature électronique).

    Workflow de validation:
    BROUILLON -> SOUMIS -> VALIDE (ou REJETE -> BROUILLON)
    """

    BROUILLON = "brouillon"  # Saisie en cours
    SOUMIS = "soumis"  # Soumis pour validation
    VALIDE = "valide"  # Validé par le responsable
    REJETE = "rejete"  # Rejeté, nécessite correction

    @classmethod
    def from_string(cls, value: str) -> "StatutPointage":
        """
        Convertit une chaîne en StatutPointage.

        Args:
            value: La valeur string.

        Returns:
            Le StatutPointage correspondant.

        Raises:
            ValueError: Si la valeur n'est pas valide.
        """
        try:
            return cls(value.lower())
        except ValueError:
            valid_values = [s.value for s in cls]
            raise ValueError(f"Statut invalide: {value}. Valeurs valides: {valid_values}")

    def can_transition_to(self, new_statut: "StatutPointage") -> bool:
        """
        Vérifie si la transition vers un nouveau statut est valide.

        Args:
            new_statut: Le statut cible.

        Returns:
            True si la transition est autorisée.
        """
        transitions = {
            StatutPointage.BROUILLON: [StatutPointage.SOUMIS],
            StatutPointage.SOUMIS: [StatutPointage.VALIDE, StatutPointage.REJETE],
            StatutPointage.VALIDE: [],  # État final
            StatutPointage.REJETE: [StatutPointage.BROUILLON],
        }
        return new_statut in transitions.get(self, [])

    def is_editable(self) -> bool:
        """Vérifie si le pointage peut être modifié."""
        return self in [StatutPointage.BROUILLON, StatutPointage.REJETE]

    def is_final(self) -> bool:
        """Vérifie si le pointage est dans un état final."""
        return self == StatutPointage.VALIDE
