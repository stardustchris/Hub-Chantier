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
    coeff_productivite: Decimal = Decimal("1.0")
    coeff_charges_ouvrier: Optional[Decimal] = None
    coeff_charges_etam: Optional[Decimal] = None
    coeff_charges_cadre: Optional[Decimal] = None
    seuil_alerte_budget_pct: Decimal = Decimal("80")
    seuil_alerte_budget_critique_pct: Decimal = Decimal("95")
    notes: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None

    def __post_init__(self) -> None:
        if not (2020 <= self.annee <= 2099):
            raise ValueError("L'annee doit etre comprise entre 2020 et 2099")
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
        if self.coeff_productivite < Decimal("0.5") or self.coeff_productivite > Decimal("2.0"):
            raise ValueError("Le coefficient de productivite doit etre entre 0.5 et 2.0")
        if self.coeff_charges_ouvrier is not None and self.coeff_charges_ouvrier < Decimal("1"):
            raise ValueError("Le coefficient charges ouvrier doit etre >= 1")
        if self.coeff_charges_etam is not None and self.coeff_charges_etam < Decimal("1"):
            raise ValueError("Le coefficient charges ETAM doit etre >= 1")
        if self.coeff_charges_cadre is not None and self.coeff_charges_cadre < Decimal("1"):
            raise ValueError("Le coefficient charges cadre doit etre >= 1")
        if self.seuil_alerte_budget_pct < Decimal("0") or self.seuil_alerte_budget_pct > Decimal("100"):
            raise ValueError("Le seuil alerte budget doit etre entre 0 et 100")
        if self.seuil_alerte_budget_critique_pct < Decimal("0") or self.seuil_alerte_budget_critique_pct > Decimal("100"):
            raise ValueError("Le seuil alerte budget critique doit etre entre 0 et 100")
        if self.seuil_alerte_budget_pct >= self.seuil_alerte_budget_critique_pct:
            raise ValueError("Le seuil alerte doit etre inferieur au seuil critique")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "couts_fixes_annuels": str(self.couts_fixes_annuels),
            "annee": self.annee,
            "coeff_frais_generaux": str(self.coeff_frais_generaux),
            "coeff_charges_patronales": str(self.coeff_charges_patronales),
            "coeff_heures_sup": str(self.coeff_heures_sup),
            "coeff_heures_sup_2": str(self.coeff_heures_sup_2),
            "coeff_productivite": str(self.coeff_productivite),
            "coeff_charges_ouvrier": str(self.coeff_charges_ouvrier) if self.coeff_charges_ouvrier is not None else None,
            "coeff_charges_etam": str(self.coeff_charges_etam) if self.coeff_charges_etam is not None else None,
            "coeff_charges_cadre": str(self.coeff_charges_cadre) if self.coeff_charges_cadre is not None else None,
            "seuil_alerte_budget_pct": str(self.seuil_alerte_budget_pct),
            "seuil_alerte_budget_critique_pct": str(self.seuil_alerte_budget_critique_pct),
            "notes": self.notes,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "updated_by": self.updated_by,
        }
