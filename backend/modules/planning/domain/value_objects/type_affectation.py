"""Value Object TypeAffectation - Type d'affectation (unique ou recurrente)."""

from enum import Enum


class TypeAffectation(str, Enum):
    """
    Enumeration des types d'affectation.

    Selon CDC Section 5 - Planning Operationnel:
    - UNIQUE: Affectation ponctuelle pour une date specifique.
    - RECURRENTE: Affectation repetee selon un pattern de jours de la semaine.

    Attributes:
        UNIQUE: Affectation pour un jour unique.
        RECURRENTE: Affectation repetee sur plusieurs jours/semaines.

    Example:
        >>> TypeAffectation.UNIQUE.value
        'unique'
        >>> TypeAffectation.is_recurrente(TypeAffectation.RECURRENTE)
        True
    """

    UNIQUE = "unique"
    RECURRENTE = "recurrente"

    def __str__(self) -> str:
        """Retourne la valeur du type."""
        return self.value

    def is_recurrente(self) -> bool:
        """
        Verifie si le type est recurrent.

        Returns:
            True si l'affectation est recurrente.
        """
        return self == TypeAffectation.RECURRENTE

    def is_unique(self) -> bool:
        """
        Verifie si le type est unique.

        Returns:
            True si l'affectation est unique.
        """
        return self == TypeAffectation.UNIQUE

    @classmethod
    def from_string(cls, value: str) -> "TypeAffectation":
        """
        Cree un TypeAffectation a partir d'une string.

        Args:
            value: La valeur string du type.

        Returns:
            L'instance TypeAffectation correspondante.

        Raises:
            ValueError: Si la valeur ne correspond a aucun type.

        Example:
            >>> TypeAffectation.from_string("unique")
            <TypeAffectation.UNIQUE: 'unique'>
        """
        try:
            return cls(value.lower().strip())
        except ValueError:
            valid_types = [t.value for t in cls]
            raise ValueError(
                f"Type d'affectation invalide: {value}. Types valides: {valid_types}"
            )

    @classmethod
    def default(cls) -> "TypeAffectation":
        """
        Retourne le type par defaut (UNIQUE).

        Returns:
            TypeAffectation.UNIQUE
        """
        return cls.UNIQUE
