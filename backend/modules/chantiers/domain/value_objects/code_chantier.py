"""Value Object CodeChantier - Identifiant unique d'un chantier."""

import re
from dataclasses import dataclass
from typing import ClassVar, Set


@dataclass(frozen=True)
class CodeChantier:
    """
    Value Object représentant le code unique d'un chantier.

    Selon CDC CHT-19: Identifiant unique (ex: A001, B023).
    Format: Une lettre majuscule suivie de 3 chiffres.

    Les codes spéciaux pour les absences sont également acceptés:
    CONGES, MALADIE, FORMATION, RTT, ABSENT.

    Attributes:
        value: Le code du chantier (ex: "A001", "CONGES").
    """

    value: str

    # Pattern de validation: lettre + 3 chiffres OU format année-nom ou année-numéro-nom
    PATTERN: ClassVar[str] = r"^([A-Z]\d{3}|\d{4}-[A-Z0-9_-]+)$"

    # Codes spéciaux pour les absences (chantiers virtuels)
    CODES_SPECIAUX: ClassVar[Set[str]] = {"CONGES", "MALADIE", "FORMATION", "RTT", "ABSENT"}

    def __post_init__(self) -> None:
        """Valide le code à la création."""
        if not self.value:
            raise ValueError("Le code chantier ne peut pas être vide")

        # Normaliser en majuscules
        normalized = self.value.upper().strip()

        # Accepter les codes spéciaux ou le pattern standard
        if normalized not in self.CODES_SPECIAUX and not re.match(self.PATTERN, self.value):
            raise ValueError(
                f"Format de code chantier invalide: {self.value}. "
                f"Format attendu: Une lettre suivie de 3 chiffres (ex: A001, B023), "
                f"format année-numéro-nom (ex: 2024-10-MONTMELIAN) "
                f"ou un code spécial ({', '.join(sorted(self.CODES_SPECIAUX))})"
            )

        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        """Retourne le code du chantier."""
        return self.value

    @property
    def is_special(self) -> bool:
        """Indique si c'est un code spécial (absence)."""
        return self.value in self.CODES_SPECIAUX

    @property
    def letter(self) -> str:
        """Retourne la lettre du code (None pour codes spéciaux)."""
        if self.is_special:
            return self.value[0]
        return self.value[0]

    @property
    def number(self) -> int:
        """Retourne la partie numérique du code (0 pour codes spéciaux)."""
        if self.is_special:
            return 0
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
