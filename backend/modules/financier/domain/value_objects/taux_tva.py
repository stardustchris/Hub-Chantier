"""Value Object pour le taux de TVA.

Taux de TVA applicables en France pour le BTP.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import List


TAUX_VALIDES: List[Decimal] = [
    Decimal("0"),
    Decimal("5.5"),
    Decimal("10"),
    Decimal("20"),
]


@dataclass(frozen=True)
class TauxTVA:
    """Représente un taux de TVA valide.

    Les taux autorisés en France sont :
    - 20% : taux normal
    - 10% : taux intermédiaire (travaux rénovation)
    - 5.5% : taux réduit (travaux amélioration énergétique)
    - 0% : exonéré / autoliquidation
    """

    taux: Decimal

    def __post_init__(self) -> None:
        """Valide que le taux est un taux TVA autorisé."""
        if self.taux not in TAUX_VALIDES:
            taux_str = ", ".join(str(t) for t in TAUX_VALIDES)
            raise ValueError(
                f"Taux de TVA invalide : {self.taux}%. "
                f"Taux autorisés : {taux_str}"
            )

    def calculer_tva(self, montant_ht: Decimal) -> Decimal:
        """Calcule le montant de TVA sur un montant HT.

        Args:
            montant_ht: Le montant hors taxes.

        Returns:
            Le montant de TVA.
        """
        return montant_ht * self.taux / Decimal("100")

    def calculer_ttc(self, montant_ht: Decimal) -> Decimal:
        """Calcule le montant TTC à partir d'un montant HT.

        Args:
            montant_ht: Le montant hors taxes.

        Returns:
            Le montant toutes taxes comprises.
        """
        return montant_ht + self.calculer_tva(montant_ht)

    @classmethod
    def taux_normal(cls) -> "TauxTVA":
        """Retourne le taux normal (20%)."""
        return cls(taux=Decimal("20"))

    @classmethod
    def taux_intermediaire(cls) -> "TauxTVA":
        """Retourne le taux intermédiaire (10%)."""
        return cls(taux=Decimal("10"))

    @classmethod
    def taux_reduit(cls) -> "TauxTVA":
        """Retourne le taux réduit (5.5%)."""
        return cls(taux=Decimal("5.5"))

    @classmethod
    def taux_zero(cls) -> "TauxTVA":
        """Retourne le taux zéro (0%)."""
        return cls(taux=Decimal("0"))
