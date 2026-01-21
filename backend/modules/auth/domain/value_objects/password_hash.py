"""Value Object PasswordHash - Représente un mot de passe hashé."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PasswordHash:
    """
    Value Object représentant un mot de passe hashé.

    Ne contient JAMAIS le mot de passe en clair.
    Immutable par design.

    Attributes:
        value: Le hash du mot de passe.
    """

    value: str

    def __post_init__(self) -> None:
        """Valide que le hash n'est pas vide."""
        if not self.value:
            raise ValueError("Le hash du mot de passe ne peut pas être vide")

    def __str__(self) -> str:
        """Ne jamais exposer le hash dans les logs."""
        return "***HIDDEN***"

    def __repr__(self) -> str:
        """Représentation sécurisée."""
        return "PasswordHash(***)"
