"""DTOs pour les alertes de depassement budgetaire.

FIN-12: Alertes depassements.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.alerte_depassement import AlerteDepassement


@dataclass
class AlerteCreateDTO:
    """DTO pour la creation d'une alerte de depassement."""

    chantier_id: int
    budget_id: int
    type_alerte: str
    message: str
    pourcentage_atteint: Decimal
    seuil_configure: Decimal
    montant_budget_ht: Decimal
    montant_atteint_ht: Decimal


@dataclass
class AlerteDTO:
    """DTO de sortie pour une alerte de depassement."""

    id: int
    chantier_id: int
    budget_id: int
    type_alerte: str
    message: str
    pourcentage_atteint: str
    seuil_configure: str
    montant_budget_ht: str
    montant_atteint_ht: str
    est_acquittee: bool
    acquittee_par: Optional[int]
    acquittee_at: Optional[datetime]
    created_at: Optional[datetime]

    @classmethod
    def from_entity(cls, alerte: AlerteDepassement) -> AlerteDTO:
        """Cree un DTO depuis une entite AlerteDepassement.

        Args:
            alerte: L'entite AlerteDepassement source.

        Returns:
            Le DTO de sortie.
        """
        return cls(
            id=alerte.id,
            chantier_id=alerte.chantier_id,
            budget_id=alerte.budget_id,
            type_alerte=alerte.type_alerte,
            message=alerte.message,
            pourcentage_atteint=str(alerte.pourcentage_atteint),
            seuil_configure=str(alerte.seuil_configure),
            montant_budget_ht=str(alerte.montant_budget_ht),
            montant_atteint_ht=str(alerte.montant_atteint_ht),
            est_acquittee=alerte.est_acquittee,
            acquittee_par=alerte.acquittee_par,
            acquittee_at=alerte.acquittee_at,
            created_at=alerte.created_at,
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "chantier_id": self.chantier_id,
            "budget_id": self.budget_id,
            "type_alerte": self.type_alerte,
            "message": self.message,
            "pourcentage_atteint": self.pourcentage_atteint,
            "seuil_configure": self.seuil_configure,
            "montant_budget_ht": self.montant_budget_ht,
            "montant_atteint_ht": self.montant_atteint_ht,
            "est_acquittee": self.est_acquittee,
            "acquittee_par": self.acquittee_par,
            "acquittee_at": (
                self.acquittee_at.isoformat() if self.acquittee_at else None
            ),
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
        }
