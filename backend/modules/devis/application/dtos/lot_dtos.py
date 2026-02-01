"""DTOs pour les lots de devis.

DEV-03: Creation devis structure - Arborescence par lots.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING

from .ligne_dtos import LigneDevisDTO

if TYPE_CHECKING:
    from ...domain.entities.lot_devis import LotDevis


@dataclass
class LotDevisCreateDTO:
    """DTO pour la creation d'un lot de devis."""

    devis_id: int
    titre: str
    numero: str = ""
    ordre: int = 0
    marge_lot_pct: Optional[Decimal] = None


@dataclass
class LotDevisUpdateDTO:
    """DTO pour la mise a jour d'un lot de devis."""

    titre: Optional[str] = None
    numero: Optional[str] = None
    ordre: Optional[int] = None
    marge_lot_pct: Optional[Decimal] = None


@dataclass
class LotDevisDTO:
    """DTO de sortie pour un lot de devis."""

    id: int
    devis_id: int
    titre: str
    numero: str
    ordre: int
    marge_lot_pct: Optional[str]
    total_ht: str
    total_ttc: str
    debourse_sec: str
    lignes: List[LigneDevisDTO]

    @classmethod
    def from_entity(
        cls,
        lot: LotDevis,
        lignes: Optional[List[LigneDevisDTO]] = None,
    ) -> LotDevisDTO:
        """Cree un DTO depuis une entite LotDevis."""
        return cls(
            id=lot.id,
            devis_id=lot.devis_id,
            titre=lot.titre,
            numero=lot.numero,
            ordre=lot.ordre,
            marge_lot_pct=str(lot.marge_lot_pct) if lot.marge_lot_pct is not None else None,
            total_ht=str(lot.total_ht),
            total_ttc=str(lot.total_ttc),
            debourse_sec=str(lot.debourse_sec),
            lignes=lignes or [],
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "devis_id": self.devis_id,
            "titre": self.titre,
            "numero": self.numero,
            "ordre": self.ordre,
            "marge_lot_pct": self.marge_lot_pct,
            "total_ht": self.total_ht,
            "total_ttc": self.total_ttc,
            "debourse_sec": self.debourse_sec,
            "lignes": [l.to_dict() for l in self.lignes],
        }
