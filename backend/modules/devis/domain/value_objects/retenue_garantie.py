"""Value Object pour la retenue de garantie.

DEV-22: Parametrage retenue de garantie par devis (0%, 5%, 10%).
"""

from decimal import Decimal
from typing import Tuple


class RetenueGarantieInvalideError(ValueError):
    """Erreur levee quand le taux de retenue de garantie n'est pas autorise."""

    TAUX_AUTORISES: Tuple[int, ...] = (0, 5, 10)

    def __init__(self, taux: Decimal):
        self.taux = taux
        taux_str = ", ".join(str(t) for t in self.TAUX_AUTORISES)
        super().__init__(
            f"Taux de retenue de garantie invalide: {taux}%. "
            f"Valeurs autorisees: {taux_str}%"
        )


class RetenueGarantie:
    """Value Object representant une retenue de garantie.

    La retenue de garantie est un pourcentage retenu sur le montant TTC
    du devis, restitue au prestataire apres la levee des reserves.

    Valeurs autorisees: 0%, 5%, 10%.

    Attributes:
        taux: Le taux de retenue en pourcentage (0, 5 ou 10).
    """

    TAUX_AUTORISES: Tuple[Decimal, ...] = (
        Decimal("0"),
        Decimal("5"),
        Decimal("10"),
    )

    def __init__(self, taux: Decimal) -> None:
        """Initialise la retenue de garantie.

        Args:
            taux: Le taux de retenue en pourcentage.

        Raises:
            RetenueGarantieInvalideError: Si le taux n'est pas dans {0, 5, 10}.
        """
        # Normaliser le taux en Decimal
        taux_decimal = Decimal(str(taux))

        if taux_decimal not in self.TAUX_AUTORISES:
            raise RetenueGarantieInvalideError(taux_decimal)

        self._taux = taux_decimal

    @property
    def taux(self) -> Decimal:
        """Retourne le taux de retenue en pourcentage."""
        return self._taux

    def calculer_montant(self, montant_ttc: Decimal) -> Decimal:
        """Calcule le montant de la retenue de garantie.

        Args:
            montant_ttc: Le montant TTC du devis.

        Returns:
            Le montant retenu (montant_ttc * taux / 100).
        """
        return (montant_ttc * self._taux / Decimal("100")).quantize(Decimal("0.01"))

    def montant_net_a_payer(self, montant_ttc: Decimal) -> Decimal:
        """Calcule le montant net a payer apres retenue.

        Args:
            montant_ttc: Le montant TTC du devis.

        Returns:
            Le montant net (TTC - retenue de garantie).
        """
        return montant_ttc - self.calculer_montant(montant_ttc)

    def __eq__(self, other: object) -> bool:
        """Egalite basee sur le taux."""
        if not isinstance(other, RetenueGarantie):
            return False
        return self._taux == other._taux

    def __hash__(self) -> int:
        """Hash base sur le taux."""
        return hash(self._taux)

    def __repr__(self) -> str:
        return f"RetenueGarantie(taux={self._taux}%)"

    def __str__(self) -> str:
        return f"{self._taux}%"
