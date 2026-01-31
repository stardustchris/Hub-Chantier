"""DTOs pour les avenants budgétaires.

FIN-04: Avenants budgétaires - Modifications du budget initial.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.avenant_budgetaire import AvenantBudgetaire


@dataclass
class AvenantCreateDTO:
    """DTO pour la création d'un avenant budgétaire."""

    budget_id: int
    motif: str
    montant_ht: Decimal = Decimal("0")
    impact_description: Optional[str] = None


@dataclass
class AvenantUpdateDTO:
    """DTO pour la mise à jour d'un avenant budgétaire."""

    motif: Optional[str] = None
    montant_ht: Optional[Decimal] = None
    impact_description: Optional[str] = None


@dataclass
class AvenantDTO:
    """DTO de sortie pour un avenant budgétaire."""

    id: int
    budget_id: int
    numero: str
    motif: str
    montant_ht: str
    impact_description: Optional[str]
    statut: str
    created_by: Optional[int]
    validated_by: Optional[int]
    validated_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    @classmethod
    def from_entity(cls, avenant: AvenantBudgetaire) -> AvenantDTO:
        """Crée un DTO depuis une entité AvenantBudgetaire.

        Args:
            avenant: L'entité AvenantBudgetaire source.

        Returns:
            Le DTO de sortie.
        """
        return cls(
            id=avenant.id,
            budget_id=avenant.budget_id,
            numero=avenant.numero,
            motif=avenant.motif,
            montant_ht=str(avenant.montant_ht),
            impact_description=avenant.impact_description,
            statut=avenant.statut,
            created_by=avenant.created_by,
            validated_by=avenant.validated_by,
            validated_at=avenant.validated_at,
            created_at=avenant.created_at,
            updated_at=avenant.updated_at,
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "budget_id": self.budget_id,
            "numero": self.numero,
            "motif": self.motif,
            "montant_ht": self.montant_ht,
            "impact_description": self.impact_description,
            "statut": self.statut,
            "created_by": self.created_by,
            "validated_by": self.validated_by,
            "validated_at": self.validated_at.isoformat() if self.validated_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
