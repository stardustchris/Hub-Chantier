"""DTOs pour la creation de devis structure.

DEV-03: Creation devis structure - Arborescence lots/chapitres/sous-chapitres/lignes.
Permet la creation en batch d'une arborescence complete.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING

from .debourse_dtos import DebourseDetailCreateDTO, DebourseDetailDTO
from .ligne_dtos import LigneDevisDTO
from .lot_dtos import LotDevisDTO

if TYPE_CHECKING:
    pass


@dataclass
class LigneStructureDTO:
    """DTO pour une ligne dans la creation de structure."""

    designation: str
    unite: str = "U"
    quantite: Decimal = Decimal("0")
    prix_unitaire_ht: Decimal = Decimal("0")
    taux_tva: Decimal = Decimal("20")
    marge_ligne_pct: Optional[Decimal] = None
    article_id: Optional[int] = None
    debourses: List[DebourseDetailCreateDTO] = field(default_factory=list)


@dataclass
class SousChapitreStructureDTO:
    """DTO pour un sous-chapitre dans la creation de structure."""

    titre: str
    marge_lot_pct: Optional[Decimal] = None
    lignes: List[LigneStructureDTO] = field(default_factory=list)


@dataclass
class LotStructureDTO:
    """DTO pour un lot dans la creation de structure.

    Supporte les sous-chapitres imbriques.
    """

    titre: str
    marge_lot_pct: Optional[Decimal] = None
    lignes: List[LigneStructureDTO] = field(default_factory=list)
    sous_chapitres: List[SousChapitreStructureDTO] = field(default_factory=list)


@dataclass
class CreateDevisStructureDTO:
    """DTO pour la creation d'une arborescence complete de devis.

    DEV-03: Permet de creer en une seule operation toute la structure:
    - Lots racine
    - Sous-chapitres par lot
    - Lignes par lot/sous-chapitre
    - Debourses par ligne
    """

    devis_id: int
    lots: List[LotStructureDTO] = field(default_factory=list)


@dataclass
class ReorderItemDTO:
    """DTO pour le reordonnement d'un element (lot ou ligne).

    DEV-03: Reorganisation par drag & drop.
    """

    id: int
    ordre: int


@dataclass
class ReorderRequestDTO:
    """DTO pour le reordonnement en batch."""

    devis_id: int
    items: List[ReorderItemDTO] = field(default_factory=list)


@dataclass
class StructureDevisDTO:
    """DTO de sortie representant la structure complete du devis.

    Arborescence complete avec lots, sous-chapitres, lignes,
    numerotation automatique et totaux.
    """

    devis_id: int
    lots: List[LotDevisDTO]
    nombre_lots: int
    nombre_lignes: int
    total_debourse_sec: str
    total_ht: str
    total_ttc: str

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "devis_id": self.devis_id,
            "lots": [lot.to_dict() for lot in self.lots],
            "nombre_lots": self.nombre_lots,
            "nombre_lignes": self.nombre_lignes,
            "total_debourse_sec": self.total_debourse_sec,
            "total_ht": self.total_ht,
            "total_ttc": self.total_ttc,
        }
