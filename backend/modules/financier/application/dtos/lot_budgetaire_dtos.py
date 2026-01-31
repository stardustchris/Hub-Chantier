"""DTOs pour les lots budgétaires.

FIN-02: Décomposition en lots - Structure arborescente du budget.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING

from ...domain.value_objects import UniteMesure

if TYPE_CHECKING:
    from ...domain.entities import LotBudgetaire


@dataclass
class LotBudgetaireCreateDTO:
    """DTO pour la création d'un lot budgétaire."""

    budget_id: int
    code_lot: str
    libelle: str
    unite: UniteMesure = UniteMesure.U
    quantite_prevue: Decimal = Decimal("0")
    prix_unitaire_ht: Decimal = Decimal("0")
    parent_lot_id: Optional[int] = None
    ordre: int = 0


@dataclass
class LotBudgetaireUpdateDTO:
    """DTO pour la mise à jour d'un lot budgétaire."""

    code_lot: Optional[str] = None
    libelle: Optional[str] = None
    unite: Optional[UniteMesure] = None
    quantite_prevue: Optional[Decimal] = None
    prix_unitaire_ht: Optional[Decimal] = None
    parent_lot_id: Optional[int] = None
    ordre: Optional[int] = None


@dataclass
class LotBudgetaireDTO:
    """DTO de sortie pour un lot budgétaire.

    Inclut les montants engagé et réalisé calculés depuis les achats.
    """

    id: int
    budget_id: int
    code_lot: str
    libelle: str
    unite: str
    unite_label: str
    quantite_prevue: str
    prix_unitaire_ht: str
    total_prevu_ht: str
    engage: str
    realise: str
    ecart: str
    parent_lot_id: Optional[int]
    ordre: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[int]

    @classmethod
    def from_entity(
        cls,
        lot: LotBudgetaire,
        engage: Decimal = Decimal("0"),
        realise: Decimal = Decimal("0"),
    ) -> LotBudgetaireDTO:
        """Crée un DTO depuis une entité LotBudgetaire.

        Args:
            lot: L'entité LotBudgetaire source.
            engage: Montant total engagé (achats validés/commandés/livrés/facturés).
            realise: Montant total réalisé (achats facturés).

        Returns:
            Le DTO de sortie.
        """
        ecart = lot.total_prevu_ht - engage
        return cls(
            id=lot.id,
            budget_id=lot.budget_id,
            code_lot=lot.code_lot,
            libelle=lot.libelle,
            unite=lot.unite.value,
            unite_label=lot.unite.label,
            quantite_prevue=str(lot.quantite_prevue),
            prix_unitaire_ht=str(lot.prix_unitaire_ht),
            total_prevu_ht=str(lot.total_prevu_ht),
            engage=str(engage),
            realise=str(realise),
            ecart=str(ecart),
            parent_lot_id=lot.parent_lot_id,
            ordre=lot.ordre,
            created_at=lot.created_at,
            updated_at=lot.updated_at,
            created_by=lot.created_by,
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "budget_id": self.budget_id,
            "code_lot": self.code_lot,
            "libelle": self.libelle,
            "unite": self.unite,
            "unite_label": self.unite_label,
            "quantite_prevue": self.quantite_prevue,
            "prix_unitaire_ht": self.prix_unitaire_ht,
            "total_prevu_ht": self.total_prevu_ht,
            "engage": self.engage,
            "realise": self.realise,
            "ecart": self.ecart,
            "parent_lot_id": self.parent_lot_id,
            "ordre": self.ordre,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "created_by": self.created_by,
        }


@dataclass
class LotBudgetaireListDTO:
    """DTO pour une liste paginée de lots budgétaires."""

    items: List[LotBudgetaireDTO]
    total: int
    limit: int
    offset: int

    @property
    def has_more(self) -> bool:
        """Indique s'il y a plus de résultats."""
        return self.offset + len(self.items) < self.total
