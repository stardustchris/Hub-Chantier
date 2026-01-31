"""DTOs pour les budgets.

FIN-01: Budget prévisionnel - Enveloppe budgétaire par chantier.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities import Budget


@dataclass
class BudgetCreateDTO:
    """DTO pour la création d'un budget."""

    chantier_id: int
    montant_initial_ht: Decimal = Decimal("0")
    retenue_garantie_pct: Decimal = Decimal("5")
    seuil_alerte_pct: Decimal = Decimal("80")
    seuil_validation_achat: Decimal = Decimal("1000")
    notes: Optional[str] = None


@dataclass
class BudgetUpdateDTO:
    """DTO pour la mise à jour d'un budget."""

    montant_initial_ht: Optional[Decimal] = None
    montant_avenants_ht: Optional[Decimal] = None
    retenue_garantie_pct: Optional[Decimal] = None
    seuil_alerte_pct: Optional[Decimal] = None
    seuil_validation_achat: Optional[Decimal] = None
    notes: Optional[str] = None


@dataclass
class BudgetDTO:
    """DTO de sortie pour un budget."""

    id: int
    chantier_id: int
    montant_initial_ht: str
    montant_avenants_ht: str
    montant_revise_ht: str
    retenue_garantie_pct: str
    seuil_alerte_pct: str
    seuil_validation_achat: str
    notes: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[int]

    @classmethod
    def from_entity(cls, budget: Budget) -> BudgetDTO:
        """Crée un DTO depuis une entité Budget.

        Args:
            budget: L'entité Budget source.

        Returns:
            Le DTO de sortie.
        """
        return cls(
            id=budget.id,
            chantier_id=budget.chantier_id,
            montant_initial_ht=str(budget.montant_initial_ht),
            montant_avenants_ht=str(budget.montant_avenants_ht),
            montant_revise_ht=str(budget.montant_revise_ht),
            retenue_garantie_pct=str(budget.retenue_garantie_pct),
            seuil_alerte_pct=str(budget.seuil_alerte_pct),
            seuil_validation_achat=str(budget.seuil_validation_achat),
            notes=budget.notes,
            created_at=budget.created_at,
            updated_at=budget.updated_at,
            created_by=budget.created_by,
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "chantier_id": self.chantier_id,
            "montant_initial_ht": self.montant_initial_ht,
            "montant_avenants_ht": self.montant_avenants_ht,
            "montant_revise_ht": self.montant_revise_ht,
            "retenue_garantie_pct": self.retenue_garantie_pct,
            "seuil_alerte_pct": self.seuil_alerte_pct,
            "seuil_validation_achat": self.seuil_validation_achat,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }


@dataclass
class BudgetSummaryDTO:
    """DTO résumé pour le dashboard financier.

    FIN-11: Tableau de bord financier.
    """

    budget_id: int
    chantier_id: int
    chantier_nom: Optional[str]
    montant_revise_ht: str
    total_engage: str
    total_realise: str
    marge_estimee: str

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "budget_id": self.budget_id,
            "chantier_id": self.chantier_id,
            "chantier_nom": self.chantier_nom,
            "montant_revise_ht": self.montant_revise_ht,
            "total_engage": self.total_engage,
            "total_realise": self.total_realise,
            "marge_estimee": self.marge_estimee,
        }
