"""Entite ConfigurationEntreprise - Parametres financiers configurables."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class ConfigurationEntreprise:
    """Parametres financiers de l'entreprise.

    Permet de configurer les coefficients financiers et couts fixes
    sans modifier le code. Une seule ligne par annee (UNIQUE).
    """

    id: Optional[int] = None
    couts_fixes_annuels: Decimal = Decimal("600000")
    annee: int = 2026
    # Coefficients financiers (anciennement hardcodes dans calcul_financier.py)
    coeff_frais_generaux: Decimal = Decimal("19")
    coeff_charges_patronales: Decimal = Decimal("1.45")
    coeff_heures_sup: Decimal = Decimal("1.25")
    coeff_heures_sup_2: Decimal = Decimal("1.50")
    notes: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None

    def __post_init__(self) -> None:
        if self.couts_fixes_annuels < Decimal("0"):
            raise ValueError("Les couts fixes annuels ne peuvent pas etre negatifs")
        if self.coeff_frais_generaux < Decimal("0") or self.coeff_frais_generaux > Decimal("100"):
            raise ValueError("Le coefficient de frais generaux doit etre entre 0 et 100")
        if self.coeff_charges_patronales < Decimal("1"):
            raise ValueError("Le coefficient de charges patronales doit etre >= 1")
        if self.coeff_heures_sup < Decimal("1"):
            raise ValueError("Le coefficient heures sup doit etre >= 1")
        if self.coeff_heures_sup_2 < Decimal("1"):
            raise ValueError("Le coefficient heures sup 2 doit etre >= 1")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "couts_fixes_annuels": str(self.couts_fixes_annuels),
            "annee": self.annee,
            "coeff_frais_generaux": str(self.coeff_frais_generaux),
            "coeff_charges_patronales": str(self.coeff_charges_patronales),
            "coeff_heures_sup": str(self.coeff_heures_sup),
            "coeff_heures_sup_2": str(self.coeff_heures_sup_2),
            "notes": self.notes,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "updated_by": self.updated_by,
        }
