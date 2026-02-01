"""DTOs pour les devis.

DEV-03: Creation devis structure.
DEV-15: Suivi statut devis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING

from .lot_dtos import LotDevisDTO

if TYPE_CHECKING:
    from ...domain.entities.devis import Devis


@dataclass
class DevisCreateDTO:
    """DTO pour la creation d'un devis."""

    client_nom: str
    objet: str
    chantier_id: Optional[int] = None
    client_adresse: Optional[str] = None
    client_email: Optional[str] = None
    client_telephone: Optional[str] = None
    date_validite: Optional[date] = None
    taux_tva_defaut: Decimal = Decimal("20")
    marge_globale_pct: Decimal = Decimal("15")
    marge_moe_pct: Optional[Decimal] = None
    marge_materiaux_pct: Optional[Decimal] = None
    marge_sous_traitance_pct: Optional[Decimal] = None
    coeff_frais_generaux: Decimal = Decimal("0.12")
    retenue_garantie_pct: Decimal = Decimal("0")
    notes: Optional[str] = None
    commercial_id: Optional[int] = None


@dataclass
class DevisUpdateDTO:
    """DTO pour la mise a jour d'un devis."""

    client_nom: Optional[str] = None
    objet: Optional[str] = None
    chantier_id: Optional[int] = None
    client_adresse: Optional[str] = None
    client_email: Optional[str] = None
    client_telephone: Optional[str] = None
    date_validite: Optional[date] = None
    taux_tva_defaut: Optional[Decimal] = None
    marge_globale_pct: Optional[Decimal] = None
    marge_moe_pct: Optional[Decimal] = None
    marge_materiaux_pct: Optional[Decimal] = None
    marge_sous_traitance_pct: Optional[Decimal] = None
    coeff_frais_generaux: Optional[Decimal] = None
    retenue_garantie_pct: Optional[Decimal] = None
    notes: Optional[str] = None
    commercial_id: Optional[int] = None


@dataclass
class DevisDTO:
    """DTO de sortie resume pour un devis (liste)."""

    id: int
    numero: str
    client_nom: str
    objet: str
    statut: str
    total_ht: str
    total_ttc: str
    date_creation: Optional[str]
    date_validite: Optional[str]
    commercial_id: Optional[int]
    chantier_id: Optional[int]

    @classmethod
    def from_entity(cls, devis: Devis) -> DevisDTO:
        """Cree un DTO resume depuis une entite Devis."""
        return cls(
            id=devis.id,
            numero=devis.numero,
            client_nom=devis.client_nom,
            objet=devis.objet,
            statut=devis.statut,
            total_ht=str(devis.total_ht),
            total_ttc=str(devis.total_ttc),
            date_creation=devis.created_at.isoformat() if devis.created_at else None,
            date_validite=devis.date_validite.isoformat() if devis.date_validite else None,
            commercial_id=devis.commercial_id,
            chantier_id=devis.chantier_id,
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "numero": self.numero,
            "client_nom": self.client_nom,
            "objet": self.objet,
            "statut": self.statut,
            "total_ht": self.total_ht,
            "total_ttc": self.total_ttc,
            "date_creation": self.date_creation,
            "date_validite": self.date_validite,
            "commercial_id": self.commercial_id,
            "chantier_id": self.chantier_id,
        }


@dataclass
class DevisDetailDTO:
    """DTO de sortie detaille pour un devis (avec lots et lignes)."""

    id: int
    numero: str
    client_nom: str
    client_adresse: Optional[str]
    client_email: Optional[str]
    client_telephone: Optional[str]
    objet: str
    statut: str
    total_ht: str
    total_ttc: str
    debourse_sec_total: str
    marge_globale_pct: str
    marge_moe_pct: Optional[str]
    marge_materiaux_pct: Optional[str]
    marge_sous_traitance_pct: Optional[str]
    coeff_frais_generaux: str
    retenue_garantie_pct: str
    taux_tva_defaut: str
    date_creation: Optional[str]
    date_validite: Optional[str]
    updated_at: Optional[str]
    commercial_id: Optional[int]
    chantier_id: Optional[int]
    created_by: Optional[int]
    notes: Optional[str]
    lots: List[LotDevisDTO]

    @classmethod
    def from_entity(
        cls,
        devis: Devis,
        lots: Optional[List[LotDevisDTO]] = None,
    ) -> DevisDetailDTO:
        """Cree un DTO detaille depuis une entite Devis."""
        return cls(
            id=devis.id,
            numero=devis.numero,
            client_nom=devis.client_nom,
            client_adresse=devis.client_adresse,
            client_email=devis.client_email,
            client_telephone=devis.client_telephone,
            objet=devis.objet,
            statut=devis.statut,
            total_ht=str(devis.total_ht),
            total_ttc=str(devis.total_ttc),
            debourse_sec_total=str(devis.debourse_sec_total),
            marge_globale_pct=str(devis.marge_globale_pct),
            marge_moe_pct=str(devis.marge_moe_pct) if devis.marge_moe_pct is not None else None,
            marge_materiaux_pct=str(devis.marge_materiaux_pct) if devis.marge_materiaux_pct is not None else None,
            marge_sous_traitance_pct=str(devis.marge_sous_traitance_pct) if devis.marge_sous_traitance_pct is not None else None,
            coeff_frais_generaux=str(devis.coeff_frais_generaux),
            retenue_garantie_pct=str(devis.retenue_garantie_pct),
            taux_tva_defaut=str(devis.taux_tva_defaut),
            date_creation=devis.created_at.isoformat() if devis.created_at else None,
            date_validite=devis.date_validite.isoformat() if devis.date_validite else None,
            updated_at=devis.updated_at.isoformat() if devis.updated_at else None,
            commercial_id=devis.commercial_id,
            chantier_id=devis.chantier_id,
            created_by=devis.created_by,
            notes=devis.notes,
            lots=lots or [],
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "numero": self.numero,
            "client_nom": self.client_nom,
            "client_adresse": self.client_adresse,
            "client_email": self.client_email,
            "client_telephone": self.client_telephone,
            "objet": self.objet,
            "statut": self.statut,
            "total_ht": self.total_ht,
            "total_ttc": self.total_ttc,
            "debourse_sec_total": self.debourse_sec_total,
            "marge_globale_pct": self.marge_globale_pct,
            "marge_moe_pct": self.marge_moe_pct,
            "marge_materiaux_pct": self.marge_materiaux_pct,
            "marge_sous_traitance_pct": self.marge_sous_traitance_pct,
            "coeff_frais_generaux": self.coeff_frais_generaux,
            "retenue_garantie_pct": self.retenue_garantie_pct,
            "taux_tva_defaut": self.taux_tva_defaut,
            "date_creation": self.date_creation,
            "date_validite": self.date_validite,
            "updated_at": self.updated_at,
            "commercial_id": self.commercial_id,
            "chantier_id": self.chantier_id,
            "created_by": self.created_by,
            "notes": self.notes,
            "lots": [l.to_dict() for l in self.lots],
        }


@dataclass
class DevisListDTO:
    """DTO pour la liste paginee de devis."""

    items: List[DevisDTO]
    total: int
    limit: int
    offset: int
