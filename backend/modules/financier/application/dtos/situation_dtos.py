"""DTOs pour les situations de travaux.

FIN-07: Situations de travaux - Etats d'avancement periodiques.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.situation_travaux import SituationTravaux
    from ...domain.entities.ligne_situation import LigneSituation


@dataclass
class LigneSituationCreateDTO:
    """DTO pour la creation d'une ligne de situation."""

    lot_budgetaire_id: int
    pourcentage_avancement: Decimal = Decimal("0")


@dataclass
class LigneSituationDTO:
    """DTO de sortie pour une ligne de situation."""

    id: int
    situation_id: int
    lot_budgetaire_id: int
    pourcentage_avancement: str
    montant_marche_ht: str
    montant_cumule_precedent_ht: str
    montant_periode_ht: str
    montant_cumule_ht: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    @classmethod
    def from_entity(cls, ligne: LigneSituation) -> LigneSituationDTO:
        """Cree un DTO depuis une entite LigneSituation.

        Args:
            ligne: L'entite LigneSituation source.

        Returns:
            Le DTO de sortie.
        """
        return cls(
            id=ligne.id,
            situation_id=ligne.situation_id,
            lot_budgetaire_id=ligne.lot_budgetaire_id,
            pourcentage_avancement=str(ligne.pourcentage_avancement),
            montant_marche_ht=str(ligne.montant_marche_ht),
            montant_cumule_precedent_ht=str(ligne.montant_cumule_precedent_ht),
            montant_periode_ht=str(ligne.montant_periode_ht),
            montant_cumule_ht=str(ligne.montant_cumule_ht),
            created_at=ligne.created_at,
            updated_at=ligne.updated_at,
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "situation_id": self.situation_id,
            "lot_budgetaire_id": self.lot_budgetaire_id,
            "pourcentage_avancement": self.pourcentage_avancement,
            "montant_marche_ht": self.montant_marche_ht,
            "montant_cumule_precedent_ht": self.montant_cumule_precedent_ht,
            "montant_periode_ht": self.montant_periode_ht,
            "montant_cumule_ht": self.montant_cumule_ht,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class SituationCreateDTO:
    """DTO pour la creation d'une situation de travaux."""

    chantier_id: int
    budget_id: int
    periode_debut: date
    periode_fin: date
    retenue_garantie_pct: Decimal = Decimal("5.00")
    taux_tva: Decimal = Decimal("20.00")
    notes: Optional[str] = None
    lignes: List[LigneSituationCreateDTO] = field(default_factory=list)


@dataclass
class SituationUpdateDTO:
    """DTO pour la mise a jour d'une situation de travaux."""

    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    retenue_garantie_pct: Optional[Decimal] = None
    taux_tva: Optional[Decimal] = None
    notes: Optional[str] = None
    lignes: Optional[List[LigneSituationCreateDTO]] = None


@dataclass
class SituationDTO:
    """DTO de sortie pour une situation de travaux."""

    id: int
    chantier_id: int
    budget_id: int
    numero: str
    periode_debut: Optional[date]
    periode_fin: Optional[date]
    montant_cumule_precedent_ht: str
    montant_periode_ht: str
    montant_cumule_ht: str
    retenue_garantie_pct: str
    taux_tva: str
    montant_retenue_garantie: str
    montant_tva: str
    montant_ttc: str
    montant_net: str
    statut: str
    notes: Optional[str]
    created_by: Optional[int]
    validated_by: Optional[int]
    validated_at: Optional[datetime]
    emise_at: Optional[datetime]
    facturee_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    lignes: List[LigneSituationDTO] = field(default_factory=list)

    @classmethod
    def from_entity(
        cls,
        situation: SituationTravaux,
        lignes: Optional[List[LigneSituation]] = None,
    ) -> SituationDTO:
        """Cree un DTO depuis une entite SituationTravaux.

        Args:
            situation: L'entite SituationTravaux source.
            lignes: Liste optionnelle des lignes de situation.

        Returns:
            Le DTO de sortie.
        """
        lignes_dto = []
        if lignes:
            lignes_dto = [LigneSituationDTO.from_entity(l) for l in lignes]

        return cls(
            id=situation.id,
            chantier_id=situation.chantier_id,
            budget_id=situation.budget_id,
            numero=situation.numero,
            periode_debut=situation.periode_debut,
            periode_fin=situation.periode_fin,
            montant_cumule_precedent_ht=str(situation.montant_cumule_precedent_ht),
            montant_periode_ht=str(situation.montant_periode_ht),
            montant_cumule_ht=str(situation.montant_cumule_ht),
            retenue_garantie_pct=str(situation.retenue_garantie_pct),
            taux_tva=str(situation.taux_tva),
            montant_retenue_garantie=str(situation.montant_retenue_garantie),
            montant_tva=str(situation.montant_tva),
            montant_ttc=str(situation.montant_ttc),
            montant_net=str(situation.montant_net),
            statut=situation.statut,
            notes=situation.notes,
            created_by=situation.created_by,
            validated_by=situation.validated_by,
            validated_at=situation.validated_at,
            emise_at=situation.emise_at,
            facturee_at=situation.facturee_at,
            created_at=situation.created_at,
            updated_at=situation.updated_at,
            lignes=lignes_dto,
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "chantier_id": self.chantier_id,
            "budget_id": self.budget_id,
            "numero": self.numero,
            "periode_debut": (
                self.periode_debut.isoformat() if self.periode_debut else None
            ),
            "periode_fin": (
                self.periode_fin.isoformat() if self.periode_fin else None
            ),
            "montant_cumule_precedent_ht": self.montant_cumule_precedent_ht,
            "montant_periode_ht": self.montant_periode_ht,
            "montant_cumule_ht": self.montant_cumule_ht,
            "retenue_garantie_pct": self.retenue_garantie_pct,
            "taux_tva": self.taux_tva,
            "montant_retenue_garantie": self.montant_retenue_garantie,
            "montant_tva": self.montant_tva,
            "montant_ttc": self.montant_ttc,
            "montant_net": self.montant_net,
            "statut": self.statut,
            "notes": self.notes,
            "created_by": self.created_by,
            "validated_by": self.validated_by,
            "validated_at": (
                self.validated_at.isoformat() if self.validated_at else None
            ),
            "emise_at": (
                self.emise_at.isoformat() if self.emise_at else None
            ),
            "facturee_at": (
                self.facturee_at.isoformat() if self.facturee_at else None
            ),
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
            "lignes": [l.to_dict() for l in self.lignes],
        }
