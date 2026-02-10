"""Value Object pour le taux de TVA.

DEV-23: Generation attestation TVA reglementaire.

En France, les travaux de renovation sur batiments de plus de 2 ans
peuvent beneficier d'un taux de TVA reduit :
- 5.5% : Renovation energetique (travaux lourds, CERFA 1301-SD)
- 10.0% : Renovation standard (travaux simples, CERFA 1300-SD)
- 20.0% : Taux standard (pas d'attestation requise)
"""

from decimal import Decimal
from typing import Optional, Tuple


class TauxTVAInvalideError(ValueError):
    """Erreur levee quand le taux de TVA n'est pas autorise."""

    TAUX_AUTORISES: Tuple[str, ...] = ("0", "5.5", "10.0", "20.0")

    def __init__(self, taux: Decimal):
        self.taux = taux
        taux_str = ", ".join(f"{t}%" for t in self.TAUX_AUTORISES)
        super().__init__(
            f"Taux de TVA invalide: {taux}%. "
            f"Valeurs autorisees: {taux_str}"
        )


class TauxTVA:
    """Value Object representant un taux de TVA reglementaire.

    Encapsule les regles metier liees aux taux de TVA applicables
    dans le BTP en France, y compris la determination du type
    d'attestation CERFA requis.

    Taux autorises:
        - 5.5% : TVA reduite (renovation energetique)
        - 10.0% : TVA intermediaire (renovation)
        - 20.0% : TVA standard

    Attributes:
        taux: Le taux de TVA en pourcentage.
    """

    TAUX_AUTORISES: Tuple[Decimal, ...] = (
        Decimal("0"),
        Decimal("5.5"),
        Decimal("10.0"),
        Decimal("20.0"),
    )

    # Mapping taux -> type CERFA
    _CERFA_MAPPING = {
        Decimal("5.5"): "1301-SD",
        Decimal("10.0"): "1300-SD",
    }

    # Mapping taux -> libelle
    _LIBELLE_MAPPING = {
        Decimal("0"): "TVA 0% (autoliquidation sous-traitance)",
        Decimal("5.5"): "TVA reduite 5.5%",
        Decimal("10.0"): "TVA intermediaire 10%",
        Decimal("20.0"): "TVA standard 20%",
    }

    def __init__(self, taux: Decimal) -> None:
        """Initialise le taux de TVA.

        Args:
            taux: Le taux de TVA en pourcentage.

        Raises:
            TauxTVAInvalideError: Si le taux n'est pas dans {5.5, 10.0, 20.0}.
        """
        taux_decimal = Decimal(str(taux))

        if taux_decimal not in self.TAUX_AUTORISES:
            raise TauxTVAInvalideError(taux_decimal)

        self._taux = taux_decimal

    @property
    def taux(self) -> Decimal:
        """Retourne le taux de TVA en pourcentage."""
        return self._taux

    @property
    def necessite_attestation(self) -> bool:
        """Indique si ce taux necessite une attestation TVA.

        Les taux reduits (< 20%) necessitent une attestation CERFA
        pour justifier l'application du taux reduit.

        Returns:
            True si le taux est inferieur a 20%.
        """
        return self._taux < Decimal("20.0")

    @property
    def type_attestation(self) -> Optional[str]:
        """Retourne le type d'attestation CERFA requis.

        Returns:
            'CERFA_1300' pour travaux simples (taux 10%),
            'CERFA_1301' pour travaux lourds (taux 5.5%),
            None pour le taux standard (20%).
        """
        cerfa = self._CERFA_MAPPING.get(self._taux)
        if cerfa is None:
            return None
        return f"CERFA_{cerfa.replace('-', '_')}"

    @property
    def type_cerfa(self) -> Optional[str]:
        """Retourne le numero CERFA requis.

        Returns:
            '1300-SD' pour travaux simples (taux 10%),
            '1301-SD' pour travaux lourds (taux 5.5%),
            None pour le taux standard (20%).
        """
        return self._CERFA_MAPPING.get(self._taux)

    @property
    def libelle(self) -> str:
        """Retourne le libelle lisible du taux de TVA.

        Returns:
            Le libelle du taux (ex: 'TVA reduite 5.5%').
        """
        return self._LIBELLE_MAPPING[self._taux]

    def calculer_montant_tva(self, montant_ht: Decimal) -> Decimal:
        """Calcule le montant de TVA.

        Args:
            montant_ht: Le montant hors taxes.

        Returns:
            Le montant de TVA (montant_ht * taux / 100).
        """
        return (montant_ht * self._taux / Decimal("100")).quantize(Decimal("0.01"))

    @staticmethod
    def taux_defaut_pour_chantier(
        type_travaux: Optional[str],
        batiment_plus_2ans: Optional[bool],
        usage_habitation: Optional[bool],
    ) -> Decimal:
        """Determine le taux TVA par defaut selon le contexte chantier.

        Regle BTP France:
        - Batiment > 2 ans + habitation + renovation energetique -> 5.5%
        - Batiment > 2 ans + habitation + renovation standard -> 10%
        - Tout le reste -> 20%

        Args:
            type_travaux: "renovation", "renovation_energetique", "construction_neuve" ou None.
            batiment_plus_2ans: True si le batiment a plus de 2 ans.
            usage_habitation: True si le batiment est a usage d'habitation.

        Returns:
            Le taux TVA par defaut en Decimal.
        """
        if not batiment_plus_2ans or not usage_habitation:
            return Decimal("20")
        if type_travaux == "renovation_energetique":
            return Decimal("5.5")
        if type_travaux == "renovation":
            return Decimal("10")
        return Decimal("20")

    def __eq__(self, other: object) -> bool:
        """Egalite basee sur le taux."""
        if not isinstance(other, TauxTVA):
            return False
        return self._taux == other._taux

    def __hash__(self) -> int:
        """Hash base sur le taux."""
        return hash(self._taux)

    def __repr__(self) -> str:
        return f"TauxTVA(taux={self._taux}%)"

    def __str__(self) -> str:
        return f"{self._taux}%"
