"""Entité LotBudgetaire - Représente un lot du budget prévisionnel.

FIN-02: Décomposition en lots - Structure arborescente du budget.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional

from ..value_objects import UniteMesure


@dataclass
class LotBudgetaire:
    """Représente un lot budgétaire d'un chantier.

    Un lot budgétaire est une ligne du devis/budget prévisionnel
    avec une quantité prévue et un prix unitaire. Les lots peuvent
    être hiérarchiques (parent_lot_id).
    """

    id: Optional[int] = None
    budget_id: int = 0
    code_lot: str = ""
    libelle: str = ""
    unite: UniteMesure = UniteMesure.U
    quantite_prevue: Decimal = Decimal("0")
    prix_unitaire_ht: Decimal = Decimal("0")
    parent_lot_id: Optional[int] = None
    ordre: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    # H10: Soft delete fields
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

    def __post_init__(self) -> None:
        """Validation à la création."""
        if not self.code_lot or not self.code_lot.strip():
            raise ValueError("Le code du lot est obligatoire")
        if not self.libelle or not self.libelle.strip():
            raise ValueError("Le libellé du lot est obligatoire")
        if self.quantite_prevue < Decimal("0"):
            raise ValueError("La quantité prévue ne peut pas être négative")
        if self.prix_unitaire_ht < Decimal("0"):
            raise ValueError("Le prix unitaire HT ne peut pas être négatif")

    @property
    def total_prevu_ht(self) -> Decimal:
        """Montant total prévu HT = quantité * prix unitaire."""
        return self.quantite_prevue * self.prix_unitaire_ht

    @property
    def est_supprime(self) -> bool:
        """Vérifie si le lot a été supprimé (soft delete)."""
        return self.deleted_at is not None

    def supprimer(self, deleted_by: int) -> None:
        """Marque le lot comme supprimé (soft delete).

        Args:
            deleted_by: ID de l'utilisateur qui supprime.
        """
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by

    def to_dict(self) -> dict:
        """Convertit l'entité en dictionnaire."""
        return {
            "id": self.id,
            "budget_id": self.budget_id,
            "code_lot": self.code_lot,
            "libelle": self.libelle,
            "unite": self.unite.value,
            "quantite_prevue": str(self.quantite_prevue),
            "prix_unitaire_ht": str(self.prix_unitaire_ht),
            "total_prevu_ht": str(self.total_prevu_ht),
            "parent_lot_id": self.parent_lot_id,
            "ordre": self.ordre,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }
