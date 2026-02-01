"""DTOs pour les lignes de devis.

DEV-03 + DEV-05: Lignes de devis avec debourses.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING

from .debourse_dtos import DebourseDetailCreateDTO, DebourseDetailDTO

if TYPE_CHECKING:
    from ...domain.entities.ligne_devis import LigneDevis


@dataclass
class LigneDevisCreateDTO:
    """DTO pour la creation d'une ligne de devis."""

    lot_devis_id: int
    designation: str
    unite: str = "U"
    quantite: Decimal = Decimal("0")
    prix_unitaire_ht: Decimal = Decimal("0")
    taux_tva: Decimal = Decimal("20")
    ordre: int = 0
    marge_ligne_pct: Optional[Decimal] = None
    article_id: Optional[int] = None
    debourses: List[DebourseDetailCreateDTO] = field(default_factory=list)


@dataclass
class LigneDevisUpdateDTO:
    """DTO pour la mise a jour d'une ligne de devis."""

    designation: Optional[str] = None
    unite: Optional[str] = None
    quantite: Optional[Decimal] = None
    prix_unitaire_ht: Optional[Decimal] = None
    taux_tva: Optional[Decimal] = None
    ordre: Optional[int] = None
    marge_ligne_pct: Optional[Decimal] = None
    article_id: Optional[int] = None
    debourses: Optional[List[DebourseDetailCreateDTO]] = None


@dataclass
class LigneDevisDTO:
    """DTO de sortie pour une ligne de devis."""

    id: int
    lot_devis_id: int
    designation: str
    unite: str
    quantite: str
    prix_unitaire_ht: str
    montant_ht: str
    taux_tva: str
    montant_ttc: str
    ordre: int
    marge_ligne_pct: Optional[str]
    article_id: Optional[int]
    debourse_sec: str
    prix_revient: str
    debourses: List[DebourseDetailDTO]

    @classmethod
    def from_entity(
        cls,
        ligne: LigneDevis,
        debourses: Optional[List[DebourseDetailDTO]] = None,
    ) -> LigneDevisDTO:
        """Cree un DTO depuis une entite LigneDevis."""
        return cls(
            id=ligne.id,
            lot_devis_id=ligne.lot_devis_id,
            designation=ligne.libelle,
            unite=ligne.unite.value if hasattr(ligne.unite, 'value') else str(ligne.unite),
            quantite=str(ligne.quantite),
            prix_unitaire_ht=str(ligne.prix_unitaire_ht),
            montant_ht=str(ligne.montant_ht),
            taux_tva=str(ligne.taux_tva),
            montant_ttc=str(ligne.montant_ttc),
            ordre=ligne.ordre,
            marge_ligne_pct=str(ligne.taux_marge_ligne) if ligne.taux_marge_ligne is not None else None,
            article_id=ligne.article_id,
            debourse_sec=str(ligne.debourse_sec),
            prix_revient=str(ligne.prix_revient),
            debourses=debourses or [],
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "lot_devis_id": self.lot_devis_id,
            "designation": self.designation,
            "unite": self.unite,
            "quantite": self.quantite,
            "prix_unitaire_ht": self.prix_unitaire_ht,
            "montant_ht": self.montant_ht,
            "taux_tva": self.taux_tva,
            "montant_ttc": self.montant_ttc,
            "ordre": self.ordre,
            "marge_ligne_pct": self.marge_ligne_pct,
            "article_id": self.article_id,
            "debourse_sec": self.debourse_sec,
            "prix_revient": self.prix_revient,
            "debourses": [d.to_dict() for d in self.debourses],
        }
