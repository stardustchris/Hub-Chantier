"""Entite AffectationTacheLot - Liaison tache <-> lot budgetaire.

FIN-03: Affectation budgets aux taches - permet le suivi croise
avancement physique (taches) vs financier (lots budgetaires).
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class AffectationTacheLot:
    """Represente une affectation entre une tache et un lot budgetaire.

    Permet de lier une tache du module taches a un lot budgetaire
    du module financier, avec un pourcentage d'affectation.

    Attributes:
        id: Identifiant unique (None si non persiste).
        chantier_id: ID du chantier (sans FK cross-module).
        tache_id: ID de la tache (sans FK cross-module).
        lot_budgetaire_id: ID du lot budgetaire.
        pourcentage_affectation: Pourcentage d'affectation (0-100).
        created_at: Date de creation.
        created_by: ID de l'utilisateur createur.
    """

    chantier_id: int
    tache_id: int
    lot_budgetaire_id: int
    pourcentage_affectation: Decimal = Decimal("100")
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    created_by: Optional[int] = None

    def __post_init__(self) -> None:
        """Valide les donnees a la creation."""
        if self.chantier_id <= 0:
            raise ValueError("L'ID du chantier est obligatoire")
        if self.tache_id <= 0:
            raise ValueError("L'ID de la tache est obligatoire")
        if self.lot_budgetaire_id <= 0:
            raise ValueError("L'ID du lot budgetaire est obligatoire")
        if self.pourcentage_affectation < Decimal("0") or self.pourcentage_affectation > Decimal("100"):
            raise ValueError(
                "Le pourcentage d'affectation doit etre entre 0 et 100"
            )

    def to_dict(self) -> dict:
        """Convertit l'entite en dictionnaire."""
        return {
            "id": self.id,
            "chantier_id": self.chantier_id,
            "tache_id": self.tache_id,
            "lot_budgetaire_id": self.lot_budgetaire_id,
            "pourcentage_affectation": str(self.pourcentage_affectation),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by,
        }

    def __eq__(self, other: object) -> bool:
        """Egalite basee sur l'ID (entite)."""
        if not isinstance(other, AffectationTacheLot):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash base sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))
