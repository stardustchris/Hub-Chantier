"""DTOs pour les factures client.

FIN-08: Facturation client - Factures generees a partir des situations.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.facture_client import FactureClient


@dataclass
class FactureCreateDTO:
    """DTO pour la creation d'une facture client."""

    chantier_id: int
    type_facture: str = "acompte"
    montant_ht: Decimal = Decimal("0")
    taux_tva: Decimal = Decimal("20.00")
    retenue_garantie_pct: Decimal = Decimal("5.00")
    situation_id: Optional[int] = None
    notes: Optional[str] = None


@dataclass
class FactureUpdateDTO:
    """DTO pour la mise a jour d'une facture client."""

    montant_ht: Optional[Decimal] = None
    taux_tva: Optional[Decimal] = None
    retenue_garantie_pct: Optional[Decimal] = None
    date_echeance: Optional[date] = None
    notes: Optional[str] = None


@dataclass
class FactureDTO:
    """DTO de sortie pour une facture client."""

    id: int
    chantier_id: int
    situation_id: Optional[int]
    numero_facture: str
    type_facture: str
    montant_ht: str
    taux_tva: str
    montant_tva: str
    montant_ttc: str
    retenue_garantie_montant: str
    montant_net: str
    date_emission: Optional[date]
    date_echeance: Optional[date]
    statut: str
    notes: Optional[str]
    created_by: Optional[int]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    @classmethod
    def from_entity(cls, facture: FactureClient) -> FactureDTO:
        """Cree un DTO depuis une entite FactureClient.

        Args:
            facture: L'entite FactureClient source.

        Returns:
            Le DTO de sortie.
        """
        return cls(
            id=facture.id,
            chantier_id=facture.chantier_id,
            situation_id=facture.situation_id,
            numero_facture=facture.numero_facture,
            type_facture=facture.type_facture,
            montant_ht=str(facture.montant_ht),
            taux_tva=str(facture.taux_tva),
            montant_tva=str(facture.montant_tva),
            montant_ttc=str(facture.montant_ttc),
            retenue_garantie_montant=str(facture.retenue_garantie_montant),
            montant_net=str(facture.montant_net),
            date_emission=facture.date_emission,
            date_echeance=facture.date_echeance,
            statut=facture.statut,
            notes=facture.notes,
            created_by=facture.created_by,
            created_at=facture.created_at,
            updated_at=facture.updated_at,
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "chantier_id": self.chantier_id,
            "situation_id": self.situation_id,
            "numero_facture": self.numero_facture,
            "type_facture": self.type_facture,
            "montant_ht": self.montant_ht,
            "taux_tva": self.taux_tva,
            "montant_tva": self.montant_tva,
            "montant_ttc": self.montant_ttc,
            "retenue_garantie_montant": self.retenue_garantie_montant,
            "montant_net": self.montant_net,
            "date_emission": (
                self.date_emission.isoformat() if self.date_emission else None
            ),
            "date_echeance": (
                self.date_echeance.isoformat() if self.date_echeance else None
            ),
            "statut": self.statut,
            "notes": self.notes,
            "created_by": self.created_by,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
        }
