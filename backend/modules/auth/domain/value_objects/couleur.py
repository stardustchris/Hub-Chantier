"""Value Object Couleur - Couleur d'identification utilisateur."""

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class Couleur:
    """
    Value Object représentant une couleur d'identification.

    Selon CDC Section 3.4 - Palette de 16 couleurs pour identification
    visuelle des utilisateurs dans planning, feuilles d'heures, etc.

    Attributes:
        value: Code hexadécimal de la couleur (ex: "#E74C3C").
    """

    value: str

    # Palette des 16 couleurs autorisées (CDC Section 3.4)
    PALETTE: ClassVar[dict[str, str]] = {
        "rouge": "#E74C3C",
        "orange": "#E67E22",
        "jaune": "#F1C40F",
        "vert_clair": "#2ECC71",
        "vert_fonce": "#27AE60",
        "marron": "#795548",
        "corail": "#FF7043",
        "magenta": "#EC407A",
        "bleu_fonce": "#2C3E50",
        "bleu_clair": "#3498DB",
        "cyan": "#1ABC9C",
        "violet": "#9B59B6",
        "rose": "#E91E63",
        "gris": "#607D8B",
        "indigo": "#3F51B5",
        "lime": "#CDDC39",
    }

    # Couleur par défaut
    DEFAULT: ClassVar[str] = "#3498DB"  # Bleu clair

    def __post_init__(self) -> None:
        """Valide la couleur à la création."""
        if not self.value:
            object.__setattr__(self, "value", self.DEFAULT)
            return

        # Normaliser en majuscules
        normalized = self.value.upper()
        if not normalized.startswith("#"):
            normalized = f"#{normalized}"

        # Vérifier le format hexadécimal
        if len(normalized) != 7:
            raise ValueError(f"Format couleur invalide: {self.value}. Attendu: #RRGGBB")

        try:
            int(normalized[1:], 16)
        except ValueError:
            raise ValueError(f"Code hexadécimal invalide: {self.value}")

        # Vérifier que la couleur fait partie de la palette
        if normalized not in [c.upper() for c in self.PALETTE.values()]:
            valid_colors = list(self.PALETTE.keys())
            raise ValueError(
                f"Couleur non autorisée: {self.value}. "
                f"Couleurs valides: {valid_colors}"
            )

        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        """Retourne le code hexadécimal."""
        return self.value

    @classmethod
    def from_name(cls, name: str) -> "Couleur":
        """
        Crée une Couleur à partir de son nom.

        Args:
            name: Nom de la couleur (ex: "rouge", "bleu_clair").

        Returns:
            L'instance Couleur correspondante.

        Raises:
            ValueError: Si le nom ne correspond à aucune couleur.
        """
        name_lower = name.lower()
        if name_lower not in cls.PALETTE:
            valid_names = list(cls.PALETTE.keys())
            raise ValueError(
                f"Nom de couleur invalide: {name}. Noms valides: {valid_names}"
            )
        return cls(cls.PALETTE[name_lower])

    @classmethod
    def default(cls) -> "Couleur":
        """Retourne la couleur par défaut (bleu clair)."""
        return cls(cls.DEFAULT)

    @classmethod
    def all_colors(cls) -> list[str]:
        """Retourne la liste de tous les codes couleur valides."""
        return list(cls.PALETTE.values())

    def get_name(self) -> str:
        """Retourne le nom de la couleur."""
        for name, code in self.PALETTE.items():
            if code.upper() == self.value.upper():
                return name
        return "unknown"
