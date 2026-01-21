"""Value Object Email - Représente une adresse email validée."""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Email:
    """
    Value Object représentant une adresse email.

    Immutable et validé à la création.

    Attributes:
        value: L'adresse email sous forme de string.

    Raises:
        ValueError: Si l'email est invalide.
    """

    value: str

    def __post_init__(self) -> None:
        """Valide l'email à la création."""
        if not self.value:
            raise ValueError("L'email ne peut pas être vide")

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, self.value):
            raise ValueError(f"Email invalide: {self.value}")

    def __str__(self) -> str:
        """Retourne l'email sous forme de string."""
        return self.value

    def __eq__(self, other: object) -> bool:
        """Comparaison par valeur (case insensitive)."""
        if not isinstance(other, Email):
            return False
        return self.value.lower() == other.value.lower()

    def __hash__(self) -> int:
        """Hash basé sur la valeur lowercase."""
        return hash(self.value.lower())
