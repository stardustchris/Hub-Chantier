"""DTOs pour les affectations taches <-> lots budgetaires.

FIN-03: Affectation budgets aux taches.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.affectation_tache_lot import AffectationTacheLot


@dataclass
class AffectationCreateDTO:
    """DTO pour la creation d'une affectation."""

    chantier_id: int
    tache_id: int
    lot_budgetaire_id: int
    pourcentage_affectation: Decimal = Decimal("100")


@dataclass
class AffectationDTO:
    """DTO de sortie pour une affectation."""

    id: int
    chantier_id: int
    tache_id: int
    lot_budgetaire_id: int
    pourcentage_affectation: str
    created_at: Optional[datetime]
    created_by: Optional[int]

    @classmethod
    def from_entity(cls, affectation: AffectationTacheLot) -> AffectationDTO:
        """Cree un DTO depuis une entite AffectationTacheLot.

        Args:
            affectation: L'entite source.

        Returns:
            Le DTO de sortie.
        """
        return cls(
            id=affectation.id,
            chantier_id=affectation.chantier_id,
            tache_id=affectation.tache_id,
            lot_budgetaire_id=affectation.lot_budgetaire_id,
            pourcentage_affectation=str(affectation.pourcentage_affectation),
            created_at=affectation.created_at,
            created_by=affectation.created_by,
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "chantier_id": self.chantier_id,
            "tache_id": self.tache_id,
            "lot_budgetaire_id": self.lot_budgetaire_id,
            "pourcentage_affectation": self.pourcentage_affectation,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by,
        }


@dataclass
class SuiviAffectationDTO:
    """DTO enrichi pour le suivi croise avancement/financier.

    Combine les donnees d'affectation avec l'avancement de la tache
    et le montant du lot budgetaire.
    """

    affectation_id: int
    tache_id: int
    tache_titre: str
    tache_statut: str
    tache_progression_pct: str
    lot_budgetaire_id: int
    lot_code: str
    lot_libelle: str
    lot_montant_prevu_ht: str
    pourcentage_affectation: str
    montant_affecte_ht: str

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "affectation_id": self.affectation_id,
            "tache_id": self.tache_id,
            "tache_titre": self.tache_titre,
            "tache_statut": self.tache_statut,
            "tache_progression_pct": self.tache_progression_pct,
            "lot_budgetaire_id": self.lot_budgetaire_id,
            "lot_code": self.lot_code,
            "lot_libelle": self.lot_libelle,
            "lot_montant_prevu_ht": self.lot_montant_prevu_ht,
            "pourcentage_affectation": self.pourcentage_affectation,
            "montant_affecte_ht": self.montant_affecte_ht,
        }
