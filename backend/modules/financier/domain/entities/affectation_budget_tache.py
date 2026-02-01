"""Entite AffectationBudgetTache - Affectation d'un lot budgetaire a une tache.

FIN-03: Affectation budgets aux taches - Lien entre lots budgetaires et taches
du chantier avec un pourcentage d'allocation.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class AffectationBudgetTache:
    """Represente l'affectation d'un lot budgetaire a une tache.

    Permet de repartir le budget d'un lot sur plusieurs taches,
    avec un pourcentage d'allocation par tache. La somme des
    allocations pour un lot ne doit pas depasser 100%.

    Attributes:
        id: Identifiant unique (None si non persiste).
        lot_budgetaire_id: ID du lot budgetaire affecte.
        tache_id: ID de la tache cible (reference cross-module, pas de FK).
        pourcentage_allocation: Pourcentage du lot alloue a la tache (0-100).
        created_at: Date de creation.
        updated_at: Date de derniere mise a jour.
    """

    lot_budgetaire_id: int
    tache_id: int
    pourcentage_allocation: Decimal
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validation a la creation.

        Raises:
            ValueError: Si lot_budgetaire_id ou tache_id invalides,
                        ou pourcentage hors limites.
        """
        if self.lot_budgetaire_id <= 0:
            raise ValueError("L'ID du lot budgetaire est obligatoire")
        if self.tache_id <= 0:
            raise ValueError("L'ID de la tache est obligatoire")
        if self.pourcentage_allocation < Decimal("0") or self.pourcentage_allocation > Decimal("100"):
            raise ValueError(
                "Le pourcentage d'allocation doit etre entre 0 et 100"
            )

    def __eq__(self, other: object) -> bool:
        """Egalite basee sur l'ID (entite)."""
        if not isinstance(other, AffectationBudgetTache):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash base sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))

    def to_dict(self) -> dict:
        """Convertit l'entite en dictionnaire."""
        return {
            "id": self.id,
            "lot_budgetaire_id": self.lot_budgetaire_id,
            "tache_id": self.tache_id,
            "pourcentage_allocation": str(self.pourcentage_allocation),
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
        }
