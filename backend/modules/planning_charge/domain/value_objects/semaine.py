"""Value Object Semaine - Represente une semaine de l'annee."""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Tuple


@dataclass(frozen=True)
class Semaine:
    """
    Value Object representant une semaine de l'annee.

    Format CDC Section 6: SXX - YYYY (ex: S30 - 2025).

    Attributes:
        annee: Annee de la semaine (ex: 2025).
        numero: Numero de la semaine (1-53).
    """

    annee: int
    numero: int

    def __post_init__(self) -> None:
        """Valide les donnees a la creation."""
        if self.annee < 2020 or self.annee > 2100:
            raise ValueError(f"Annee invalide: {self.annee}. Attendu: 2020-2100")

        if self.numero < 1 or self.numero > 53:
            raise ValueError(f"Numero de semaine invalide: {self.numero}. Attendu: 1-53")

    def __str__(self) -> str:
        """Retourne le format SXX - YYYY."""
        return f"S{self.numero:02d} - {self.annee}"

    @property
    def code(self) -> str:
        """Retourne le code court SXX-YYYY."""
        return f"S{self.numero:02d}-{self.annee}"

    @classmethod
    def from_date(cls, d: date) -> "Semaine":
        """
        Cree une Semaine a partir d'une date.

        Args:
            d: La date.

        Returns:
            La Semaine correspondante.
        """
        iso_calendar = d.isocalendar()
        return cls(annee=iso_calendar.year, numero=iso_calendar.week)

    @classmethod
    def from_code(cls, code: str) -> "Semaine":
        """
        Cree une Semaine a partir d'un code (SXX-YYYY ou SXX - YYYY).

        Args:
            code: Le code de la semaine.

        Returns:
            La Semaine correspondante.

        Raises:
            ValueError: Si le format est invalide.
        """
        code = code.replace(" ", "").upper()
        if not code.startswith("S"):
            raise ValueError(f"Format invalide: {code}. Attendu: SXX-YYYY")

        try:
            parts = code[1:].split("-")
            if len(parts) != 2:
                raise ValueError(f"Format invalide: {code}. Attendu: SXX-YYYY")

            numero = int(parts[0])
            annee = int(parts[1])
            return cls(annee=annee, numero=numero)
        except ValueError as e:
            raise ValueError(f"Format invalide: {code}. Attendu: SXX-YYYY") from e

    @classmethod
    def current(cls) -> "Semaine":
        """Retourne la semaine courante."""
        return cls.from_date(date.today())

    def date_range(self) -> Tuple[date, date]:
        """
        Retourne les dates de debut et fin de la semaine.

        Returns:
            Tuple (lundi, dimanche) de la semaine.
        """
        # Trouver le 4 janvier de l'annee (toujours dans la semaine 1 ISO)
        jan4 = date(self.annee, 1, 4)
        # Trouver le lundi de la semaine 1
        week1_monday = jan4 - timedelta(days=jan4.weekday())
        # Calculer le lundi de notre semaine
        monday = week1_monday + timedelta(weeks=self.numero - 1)
        sunday = monday + timedelta(days=6)
        return (monday, sunday)

    @property
    def lundi(self) -> date:
        """Retourne le lundi de la semaine."""
        return self.date_range()[0]

    @property
    def dimanche(self) -> date:
        """Retourne le dimanche de la semaine."""
        return self.date_range()[1]

    def next(self) -> "Semaine":
        """Retourne la semaine suivante."""
        # Aller au lundi suivant
        next_monday = self.lundi + timedelta(weeks=1)
        return Semaine.from_date(next_monday)

    def previous(self) -> "Semaine":
        """Retourne la semaine precedente."""
        # Aller au lundi precedent
        prev_monday = self.lundi - timedelta(weeks=1)
        return Semaine.from_date(prev_monday)

    def __lt__(self, other: "Semaine") -> bool:
        """Comparaison inferieur."""
        if not isinstance(other, Semaine):
            return NotImplemented
        if self.annee != other.annee:
            return self.annee < other.annee
        return self.numero < other.numero

    def __le__(self, other: "Semaine") -> bool:
        """Comparaison inferieur ou egal."""
        return self == other or self < other

    def __gt__(self, other: "Semaine") -> bool:
        """Comparaison superieur."""
        if not isinstance(other, Semaine):
            return NotImplemented
        return not self <= other

    def __ge__(self, other: "Semaine") -> bool:
        """Comparaison superieur ou egal."""
        return self == other or self > other
