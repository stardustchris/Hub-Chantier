"""DTOs pour les affectations budget-tache.

FIN-03: Affectation budgets aux taches.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.affectation_budget_tache import AffectationBudgetTache


@dataclass
class CreateAffectationDTO:
    """DTO pour la creation d'une affectation budget-tache."""

    lot_budgetaire_id: int
    tache_id: int
    pourcentage_allocation: Decimal


@dataclass
class AffectationBudgetTacheDTO:
    """DTO de sortie pour une affectation budget-tache."""

    id: int
    lot_budgetaire_id: int
    tache_id: int
    pourcentage_allocation: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    @classmethod
    def from_entity(cls, affectation: AffectationBudgetTache) -> AffectationBudgetTacheDTO:
        """Cree un DTO depuis une entite AffectationBudgetTache.

        Args:
            affectation: L'entite source.

        Returns:
            Le DTO de sortie.
        """
        return cls(
            id=affectation.id,
            lot_budgetaire_id=affectation.lot_budgetaire_id,
            tache_id=affectation.tache_id,
            pourcentage_allocation=str(affectation.pourcentage_allocation),
            created_at=affectation.created_at,
            updated_at=affectation.updated_at,
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "lot_budgetaire_id": self.lot_budgetaire_id,
            "tache_id": self.tache_id,
            "pourcentage_allocation": self.pourcentage_allocation,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
        }


@dataclass
class AffectationAvecDetailsDTO:
    """DTO de sortie pour une affectation avec details du lot budgetaire."""

    id: int
    lot_budgetaire_id: int
    tache_id: int
    pourcentage_allocation: str
    code_lot: str
    libelle_lot: str
    total_prevu_ht: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "lot_budgetaire_id": self.lot_budgetaire_id,
            "tache_id": self.tache_id,
            "pourcentage_allocation": self.pourcentage_allocation,
            "code_lot": self.code_lot,
            "libelle_lot": self.libelle_lot,
            "total_prevu_ht": self.total_prevu_ht,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
        }
