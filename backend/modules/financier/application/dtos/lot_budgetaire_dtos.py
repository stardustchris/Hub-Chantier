"""DTOs pour les lots budgétaires.

FIN-02: Décomposition en lots - Structure arborescente du budget.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID

from ...domain.value_objects import UniteMesure

if TYPE_CHECKING:
    from ...domain.entities import LotBudgetaire


@dataclass
class LotBudgetaireCreateDTO:
    """DTO pour la création d'un lot budgétaire.

    Phase Devis:
        - devis_id doit être renseigné, budget_id doit être None
        - Les champs déboursés peuvent être renseignés
        - marge_pct et prix_vente_ht sont optionnels

    Phase Chantier:
        - budget_id doit être renseigné, devis_id doit être None
        - Les champs déboursés sont optionnels
    """

    code_lot: str
    libelle: str
    budget_id: Optional[int] = None
    devis_id: Optional[UUID] = None
    unite: UniteMesure = UniteMesure.U
    quantite_prevue: Decimal = Decimal("0")
    prix_unitaire_ht: Decimal = Decimal("0")
    parent_lot_id: Optional[int] = None
    ordre: int = 0

    # Champs déboursés détaillés (phase devis)
    debourse_main_oeuvre: Optional[Decimal] = None
    debourse_materiaux: Optional[Decimal] = None
    debourse_sous_traitance: Optional[Decimal] = None
    debourse_materiel: Optional[Decimal] = None
    debourse_divers: Optional[Decimal] = None

    # Marge (phase devis)
    marge_pct: Optional[Decimal] = None
    prix_vente_ht: Optional[Decimal] = None


@dataclass
class LotBudgetaireUpdateDTO:
    """DTO pour la mise à jour d'un lot budgétaire.

    Note:
        budget_id et devis_id ne peuvent pas être modifiés après création
        (un lot ne peut pas changer de phase).
    """

    code_lot: Optional[str] = None
    libelle: Optional[str] = None
    unite: Optional[UniteMesure] = None
    quantite_prevue: Optional[Decimal] = None
    prix_unitaire_ht: Optional[Decimal] = None
    parent_lot_id: Optional[int] = None
    ordre: Optional[int] = None

    # Champs déboursés détaillés (phase devis uniquement)
    debourse_main_oeuvre: Optional[Decimal] = None
    debourse_materiaux: Optional[Decimal] = None
    debourse_sous_traitance: Optional[Decimal] = None
    debourse_materiel: Optional[Decimal] = None
    debourse_divers: Optional[Decimal] = None

    # Marge (phase devis uniquement)
    marge_pct: Optional[Decimal] = None
    prix_vente_ht: Optional[Decimal] = None


@dataclass
class LotBudgetaireDTO:
    """DTO de sortie pour un lot budgétaire.

    Inclut les montants engagé et réalisé calculés depuis les achats.
    Inclut les champs de phase devis si le lot est en phase commerciale.
    """

    id: int
    budget_id: Optional[int]
    devis_id: Optional[str]
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

    # Champs déboursés détaillés (phase devis)
    debourse_main_oeuvre: Optional[str] = None
    debourse_materiaux: Optional[str] = None
    debourse_sous_traitance: Optional[str] = None
    debourse_materiel: Optional[str] = None
    debourse_divers: Optional[str] = None
    debourse_sec_total: Optional[str] = None

    # Marge (phase devis)
    marge_pct: Optional[str] = None
    prix_vente_ht: Optional[str] = None
    prix_vente_calcule_ht: Optional[str] = None

    # Indicateur de phase
    est_en_phase_devis: bool = False

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
            devis_id=str(lot.devis_id) if lot.devis_id else None,
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
            # Champs déboursés (phase devis)
            debourse_main_oeuvre=(
                str(lot.debourse_main_oeuvre) if lot.debourse_main_oeuvre is not None else None
            ),
            debourse_materiaux=(
                str(lot.debourse_materiaux) if lot.debourse_materiaux is not None else None
            ),
            debourse_sous_traitance=(
                str(lot.debourse_sous_traitance) if lot.debourse_sous_traitance is not None else None
            ),
            debourse_materiel=(
                str(lot.debourse_materiel) if lot.debourse_materiel is not None else None
            ),
            debourse_divers=(
                str(lot.debourse_divers) if lot.debourse_divers is not None else None
            ),
            debourse_sec_total=str(lot.debourse_sec_total) if lot.est_en_phase_devis else None,
            # Marge
            marge_pct=str(lot.marge_pct) if lot.marge_pct is not None else None,
            prix_vente_ht=str(lot.prix_vente_ht) if lot.prix_vente_ht is not None else None,
            prix_vente_calcule_ht=(
                str(lot.prix_vente_calcule_ht) if lot.prix_vente_calcule_ht is not None else None
            ),
            # Indicateur
            est_en_phase_devis=lot.est_en_phase_devis,
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        result = {
            "id": self.id,
            "budget_id": self.budget_id,
            "devis_id": self.devis_id,
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
            "est_en_phase_devis": self.est_en_phase_devis,
        }

        # Ajouter les champs de phase devis s'ils sont renseignés
        if self.est_en_phase_devis:
            result.update(
                {
                    "debourse_main_oeuvre": self.debourse_main_oeuvre,
                    "debourse_materiaux": self.debourse_materiaux,
                    "debourse_sous_traitance": self.debourse_sous_traitance,
                    "debourse_materiel": self.debourse_materiel,
                    "debourse_divers": self.debourse_divers,
                    "debourse_sec_total": self.debourse_sec_total,
                    "marge_pct": self.marge_pct,
                    "prix_vente_ht": self.prix_vente_ht,
                    "prix_vente_calcule_ht": self.prix_vente_calcule_ht,
                }
            )

        return result


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
