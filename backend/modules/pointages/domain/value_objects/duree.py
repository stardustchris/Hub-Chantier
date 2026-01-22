"""Value Object Duree - Durée en heures et minutes."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Duree:
    """
    Représente une durée en heures et minutes.

    Selon CDC Section 7 - Saisie mobile HH:MM (FDH-11).

    Attributes:
        heures: Nombre d'heures (0-23).
        minutes: Nombre de minutes (0-59).
    """

    heures: int
    minutes: int

    def __post_init__(self) -> None:
        """Valide les données."""
        if self.heures < 0 or self.heures > 23:
            raise ValueError(f"Heures invalides: {self.heures}. Doit être entre 0 et 23.")
        if self.minutes < 0 or self.minutes > 59:
            raise ValueError(f"Minutes invalides: {self.minutes}. Doit être entre 0 et 59.")

    @classmethod
    def zero(cls) -> "Duree":
        """Crée une durée de zéro."""
        return cls(heures=0, minutes=0)

    @classmethod
    def from_minutes(cls, total_minutes: int) -> "Duree":
        """
        Crée une Duree à partir du nombre total de minutes.

        Args:
            total_minutes: Nombre total de minutes.

        Returns:
            Une instance de Duree.
        """
        if total_minutes < 0:
            raise ValueError("Les minutes ne peuvent pas être négatives")
        heures = min(total_minutes // 60, 23)
        minutes = total_minutes % 60
        return cls(heures=heures, minutes=minutes)

    @classmethod
    def from_decimal(cls, decimal_hours: float) -> "Duree":
        """
        Crée une Duree à partir d'heures décimales.

        Args:
            decimal_hours: Heures en décimal (ex: 7.5 = 7h30).

        Returns:
            Une instance de Duree.
        """
        if decimal_hours < 0:
            raise ValueError("Les heures ne peuvent pas être négatives")
        total_minutes = int(round(decimal_hours * 60))
        return cls.from_minutes(total_minutes)

    @classmethod
    def from_string(cls, value: str) -> "Duree":
        """
        Parse une durée depuis une chaîne HH:MM ou H:MM.

        Args:
            value: Chaîne au format HH:MM.

        Returns:
            Une instance de Duree.

        Raises:
            ValueError: Si le format est invalide.
        """
        if not value or ":" not in value:
            raise ValueError(f"Format invalide: {value}. Attendu: HH:MM")

        parts = value.strip().split(":")
        if len(parts) != 2:
            raise ValueError(f"Format invalide: {value}. Attendu: HH:MM")

        try:
            heures = int(parts[0])
            minutes = int(parts[1])
        except ValueError:
            raise ValueError(f"Format invalide: {value}. Attendu: HH:MM avec des nombres")

        return cls(heures=heures, minutes=minutes)

    @property
    def total_minutes(self) -> int:
        """Retourne le total en minutes."""
        return self.heures * 60 + self.minutes

    @property
    def decimal(self) -> float:
        """Retourne la durée en heures décimales."""
        return self.heures + self.minutes / 60

    def __str__(self) -> str:
        """Format HH:MM."""
        return f"{self.heures:02d}:{self.minutes:02d}"

    def __repr__(self) -> str:
        """Représentation debug."""
        return f"Duree({self.heures}h{self.minutes:02d})"

    def __add__(self, other: "Duree") -> "Duree":
        """Additionne deux durées."""
        total = self.total_minutes + other.total_minutes
        return Duree.from_minutes(total)

    def __sub__(self, other: "Duree") -> "Duree":
        """Soustrait deux durées."""
        total = self.total_minutes - other.total_minutes
        if total < 0:
            raise ValueError("La durée résultante ne peut pas être négative")
        return Duree.from_minutes(total)

    def __lt__(self, other: "Duree") -> bool:
        """Comparaison."""
        return self.total_minutes < other.total_minutes

    def __le__(self, other: "Duree") -> bool:
        """Comparaison."""
        return self.total_minutes <= other.total_minutes

    def __gt__(self, other: "Duree") -> bool:
        """Comparaison."""
        return self.total_minutes > other.total_minutes

    def __ge__(self, other: "Duree") -> bool:
        """Comparaison."""
        return self.total_minutes >= other.total_minutes

    def is_zero(self) -> bool:
        """Vérifie si la durée est nulle."""
        return self.total_minutes == 0
