"""Value Object HeureAffectation - Represente une heure au format HH:MM."""

from dataclasses import dataclass


@dataclass(frozen=True)
class HeureAffectation:
    """
    Value Object representant une heure d'affectation.

    Format HH:MM pour definir les horaires de debut et fin d'une affectation.

    Attributes:
        heure: L'heure (0-23).
        minute: La minute (0-59).

    Raises:
        ValueError: Si l'heure ou la minute est hors limites.

    Example:
        >>> heure = HeureAffectation(8, 30)
        >>> str(heure)
        '08:30'
    """

    heure: int
    minute: int

    def __post_init__(self) -> None:
        """Valide les valeurs a la creation."""
        if not isinstance(self.heure, int) or not isinstance(self.minute, int):
            raise ValueError("L'heure et la minute doivent etre des entiers")

        if not 0 <= self.heure <= 23:
            raise ValueError(
                f"L'heure doit etre comprise entre 0 et 23, recu: {self.heure}"
            )

        if not 0 <= self.minute <= 59:
            raise ValueError(
                f"La minute doit etre comprise entre 0 et 59, recu: {self.minute}"
            )

    def __str__(self) -> str:
        """Retourne l'heure au format HH:MM."""
        return f"{self.heure:02d}:{self.minute:02d}"

    def __lt__(self, other: "HeureAffectation") -> bool:
        """Compare deux heures (inferieur)."""
        if not isinstance(other, HeureAffectation):
            return NotImplemented
        return self.to_minutes() < other.to_minutes()

    def __le__(self, other: "HeureAffectation") -> bool:
        """Compare deux heures (inferieur ou egal)."""
        if not isinstance(other, HeureAffectation):
            return NotImplemented
        return self.to_minutes() <= other.to_minutes()

    def __gt__(self, other: "HeureAffectation") -> bool:
        """Compare deux heures (superieur)."""
        if not isinstance(other, HeureAffectation):
            return NotImplemented
        return self.to_minutes() > other.to_minutes()

    def __ge__(self, other: "HeureAffectation") -> bool:
        """Compare deux heures (superieur ou egal)."""
        if not isinstance(other, HeureAffectation):
            return NotImplemented
        return self.to_minutes() >= other.to_minutes()

    def to_minutes(self) -> int:
        """
        Convertit l'heure en nombre total de minutes.

        Returns:
            Le nombre de minutes depuis minuit.

        Example:
            >>> HeureAffectation(8, 30).to_minutes()
            510
        """
        return self.heure * 60 + self.minute

    def to_string(self) -> str:
        """
        Retourne l'heure sous forme de chaine HH:MM.

        Returns:
            La chaine au format HH:MM.
        """
        return str(self)

    @classmethod
    def from_string(cls, value: str) -> "HeureAffectation":
        """
        Cree une HeureAffectation a partir d'une chaine HH:MM.

        Args:
            value: La chaine au format HH:MM ou H:MM.

        Returns:
            L'instance HeureAffectation correspondante.

        Raises:
            ValueError: Si le format est invalide.

        Example:
            >>> heure = HeureAffectation.from_string("08:30")
            >>> heure.heure
            8
        """
        if not value or not isinstance(value, str):
            raise ValueError("La valeur doit etre une chaine non vide")

        parts = value.strip().split(":")
        if len(parts) != 2:
            raise ValueError(
                f"Format invalide: {value}. Attendu: HH:MM (ex: 08:30)"
            )

        try:
            heure = int(parts[0])
            minute = int(parts[1])
        except ValueError:
            raise ValueError(
                f"Format invalide: {value}. L'heure et la minute doivent etre des nombres"
            )

        return cls(heure=heure, minute=minute)

    @classmethod
    def debut_journee(cls) -> "HeureAffectation":
        """
        Cree une heure de debut de journee standard (08:00).

        Returns:
            HeureAffectation pour 08:00.
        """
        return cls(heure=8, minute=0)

    @classmethod
    def fin_journee(cls) -> "HeureAffectation":
        """
        Cree une heure de fin de journee standard (17:00).

        Returns:
            HeureAffectation pour 17:00.
        """
        return cls(heure=17, minute=0)

    @classmethod
    def midi(cls) -> "HeureAffectation":
        """
        Cree une heure de pause dejeuner (12:00).

        Returns:
            HeureAffectation pour 12:00.
        """
        return cls(heure=12, minute=0)

    def duree_vers(self, fin: "HeureAffectation") -> int:
        """
        Calcule la duree en minutes entre cette heure et une heure de fin.

        Args:
            fin: L'heure de fin.

        Returns:
            La duree en minutes (peut etre negatif si fin < debut).

        Example:
            >>> debut = HeureAffectation(8, 0)
            >>> fin = HeureAffectation(17, 0)
            >>> debut.duree_vers(fin)
            540
        """
        return fin.to_minutes() - self.to_minutes()
