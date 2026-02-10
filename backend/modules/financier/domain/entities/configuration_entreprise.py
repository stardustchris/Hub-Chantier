"""Entite ConfigurationEntreprise - Parametres financiers configurables."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class ConfigurationEntreprise:
    """Parametres financiers de l'entreprise.

    Permet de configurer les couts fixes annuels sans modifier le code.
    """

    id: Optional[int] = None
    couts_fixes_annuels: Decimal = Decimal("600000")
    annee: int = 2026
    notes: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None

    def __post_init__(self) -> None:
        if self.couts_fixes_annuels < Decimal("0"):
            raise ValueError("Les couts fixes annuels ne peuvent pas etre negatifs")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "couts_fixes_annuels": str(self.couts_fixes_annuels),
            "annee": self.annee,
            "notes": self.notes,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "updated_by": self.updated_by,
        }
