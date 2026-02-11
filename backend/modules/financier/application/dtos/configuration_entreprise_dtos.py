"""DTOs pour la configuration entreprise."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class ConfigurationEntrepriseDTO:
    """DTO de lecture de la configuration entreprise."""

    id: int
    couts_fixes_annuels: Decimal
    annee: int
    coeff_frais_generaux: Decimal
    coeff_charges_patronales: Decimal
    coeff_heures_sup: Decimal
    coeff_heures_sup_2: Decimal
    notes: Optional[str]
    updated_at: Optional[datetime]
    updated_by: Optional[int]


@dataclass
class ConfigurationEntrepriseUpdateDTO:
    """DTO de mise a jour de la configuration entreprise (admin only)."""

    couts_fixes_annuels: Optional[Decimal] = None
    coeff_frais_generaux: Optional[Decimal] = None
    coeff_charges_patronales: Optional[Decimal] = None
    coeff_heures_sup: Optional[Decimal] = None
    coeff_heures_sup_2: Optional[Decimal] = None
    notes: Optional[str] = None
