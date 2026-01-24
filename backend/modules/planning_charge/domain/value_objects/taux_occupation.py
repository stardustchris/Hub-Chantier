"""Value Object TauxOccupation - Taux d'occupation avec code couleur."""

from dataclasses import dataclass
from enum import Enum
from typing import ClassVar


class NiveauOccupation(Enum):
    """
    Niveau d'occupation selon les seuils CDC Section 6.4.

    < 70%: Sous-charge (vert)
    70-90%: Normal (bleu)
    90-100%: Haute (jaune/orange)
    >= 100%: Surcharge (rouge + alerte)
    > 100%: Critique (rouge fonce)
    """

    SOUS_CHARGE = "sous_charge"
    NORMAL = "normal"
    HAUTE = "haute"
    SURCHARGE = "surcharge"
    CRITIQUE = "critique"

    @property
    def couleur(self) -> str:
        """Retourne le code couleur hexadecimal."""
        couleurs = {
            "sous_charge": "#27AE60",  # Vert
            "normal": "#3498DB",  # Bleu clair
            "haute": "#F39C12",  # Jaune/Orange
            "surcharge": "#E74C3C",  # Rouge
            "critique": "#C0392B",  # Rouge fonce
        }
        return couleurs.get(self.value, "#607D8B")

    @property
    def label(self) -> str:
        """Retourne le label lisible."""
        labels = {
            "sous_charge": "Sous-charge",
            "normal": "Normal",
            "haute": "Charge haute",
            "surcharge": "Surcharge",
            "critique": "Critique",
        }
        return labels.get(self.value, self.value)

    @property
    def alerte(self) -> bool:
        """Indique si une alerte doit etre affichee."""
        return self in (NiveauOccupation.SURCHARGE, NiveauOccupation.CRITIQUE)


@dataclass(frozen=True)
class TauxOccupation:
    """
    Value Object representant un taux d'occupation.

    Selon CDC Section 6.4 - Codes couleur - Taux d'occupation.

    Attributes:
        valeur: Le taux en pourcentage (0-200+).
    """

    valeur: float

    # Seuils selon CDC Section 6.4
    SEUIL_NORMAL: ClassVar[float] = 70.0
    SEUIL_HAUTE: ClassVar[float] = 90.0
    SEUIL_SURCHARGE: ClassVar[float] = 100.0
    SEUIL_CRITIQUE: ClassVar[float] = 100.0  # Meme seuil, mais > au lieu de >=

    def __post_init__(self) -> None:
        """Valide la valeur."""
        if self.valeur < 0:
            raise ValueError(f"Taux invalide: {self.valeur}. Le taux doit etre >= 0")

    def __str__(self) -> str:
        """Retourne le taux formate."""
        return f"{self.valeur:.1f}%"

    @property
    def niveau(self) -> NiveauOccupation:
        """
        Determine le niveau d'occupation selon les seuils.

        Returns:
            Le NiveauOccupation correspondant.
        """
        if self.valeur < self.SEUIL_NORMAL:
            return NiveauOccupation.SOUS_CHARGE
        elif self.valeur < self.SEUIL_HAUTE:
            return NiveauOccupation.NORMAL
        elif self.valeur < self.SEUIL_SURCHARGE:
            return NiveauOccupation.HAUTE
        elif self.valeur == self.SEUIL_SURCHARGE:
            return NiveauOccupation.SURCHARGE
        else:
            return NiveauOccupation.CRITIQUE

    @property
    def couleur(self) -> str:
        """Retourne le code couleur hexadecimal."""
        return self.niveau.couleur

    @property
    def alerte(self) -> bool:
        """Indique si une alerte doit etre affichee (PDC-13)."""
        return self.niveau.alerte

    @property
    def label(self) -> str:
        """Retourne le label du niveau."""
        return self.niveau.label

    @classmethod
    def calculer(cls, planifie: float, capacite: float) -> "TauxOccupation":
        """
        Calcule le taux d'occupation.

        Args:
            planifie: Heures planifiees.
            capacite: Capacite disponible en heures.

        Returns:
            Le TauxOccupation calcule.
        """
        if capacite <= 0:
            return cls(0.0) if planifie <= 0 else cls(200.0)  # Critique si planifie sans capacite

        taux = (planifie / capacite) * 100.0
        return cls(taux)

    @classmethod
    def zero(cls) -> "TauxOccupation":
        """Retourne un taux nul."""
        return cls(0.0)
