"""Value Object CodeChantier - Identifiant unique d'un chantier."""

import re
from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class CodeChantier:
    """
    Value Object représentant le code unique d'un chantier.

    Selon CDC CHT-19: Identifiant unique (ex: A001, B023).
    Format: Une lettre majuscule suivie de 3 chiffres.

    Attributes:
        value: Le code du chantier (ex: "A001").
    """

    value: str

    # Pattern de validation: lettre + 3 chiffres
    PATTERN: ClassVar[str] = r"^[A-Z]\d{3}$"

    def __post_init__(self) -> None:
        """Valide le code à la création."""
        if not self.value:
            raise ValueError("Le code chantier ne peut pas être vide")

        # Normaliser en majuscules
        normalized = self.value.upper().strip()

        if not re.match(self.PATTERN, normalized):
            raise ValueError(
                f"Format de code chantier invalide: {self.value}. "
                f"Format attendu: Une lettre suivie de 3 chiffres (ex: A001, B023)"
            )

        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        """Retourne le code du chantier."""
        return self.value

    @property
    def letter(self) -> str:
        """Retourne la lettre du code."""
        return self.value[0]

    @property
    def number(self) -> int:
        """Retourne la partie numérique du code."""
        return int(self.value[1:])

    @classmethod
    def generate_next(cls, last_code: str | None) -> "CodeChantier":
        """
        Génère le prochain code à partir du dernier code.

        Args:
            last_code: Le dernier code utilisé (ou None pour démarrer).

        Returns:
            Le prochain CodeChantier.

        Examples:
            >>> CodeChantier.generate_next(None).value
            'A001'
            >>> CodeChantier.generate_next("A001").value
            'A002'
            >>> CodeChantier.generate_next("A999").value
            'B001'
            >>> CodeChantier.generate_next("Z999").value
            Raises ValueError
        """
        if last_code is None:
            return cls("A001")

        current = cls(last_code)
        letter = current.letter
        number = current.number

        if number < 999:
            # Incrémenter le numéro
            return cls(f"{letter}{number + 1:03d}")
        else:
            # Passer à la lettre suivante
            if letter == "Z":
                raise ValueError(
                    "Capacité maximale atteinte (Z999). "
                    "Impossible de générer un nouveau code."
                )
            next_letter = chr(ord(letter) + 1)
            return cls(f"{next_letter}001")

    @classmethod
    def from_string(cls, value: str) -> "CodeChantier":
        """
        Crée un CodeChantier à partir d'une chaîne.

        Args:
            value: Le code sous forme de chaîne.

        Returns:
            L'instance CodeChantier.
        """
        return cls(value)

    def __lt__(self, other: "CodeChantier") -> bool:
        """Comparaison pour tri."""
        if not isinstance(other, CodeChantier):
            return NotImplemented
        return self.value < other.value
