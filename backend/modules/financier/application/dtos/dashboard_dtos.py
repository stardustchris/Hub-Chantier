"""DTOs pour le tableau de bord financier.

FIN-11: Tableau de bord financier - KPI, stats, répartition.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional


@dataclass
class KPIFinancierDTO:
    """DTO pour les indicateurs clés financiers d'un chantier."""

    montant_revise_ht: str
    total_engage: str
    total_realise: str
    marge_estimee: str
    pct_engage: str
    pct_realise: str

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "montant_revise_ht": self.montant_revise_ht,
            "total_engage": self.total_engage,
            "total_realise": self.total_realise,
            "marge_estimee": self.marge_estimee,
            "pct_engage": self.pct_engage,
            "pct_realise": self.pct_realise,
        }


@dataclass
class DerniersAchatsDTO:
    """DTO pour les derniers achats résumés."""

    id: int
    libelle: str
    fournisseur_nom: Optional[str]
    total_ht: str
    statut: str
    statut_label: str
    statut_couleur: str
    created_at: Optional[str]

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "libelle": self.libelle,
            "fournisseur_nom": self.fournisseur_nom,
            "total_ht": self.total_ht,
            "statut": self.statut,
            "statut_label": self.statut_label,
            "statut_couleur": self.statut_couleur,
            "created_at": self.created_at,
        }


@dataclass
class RepartitionLotDTO:
    """DTO pour la répartition budgétaire par lot."""

    lot_id: int
    code_lot: str
    libelle: str
    total_prevu_ht: str
    engage: str
    realise: str
    ecart: str

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "lot_id": self.lot_id,
            "code_lot": self.code_lot,
            "libelle": self.libelle,
            "total_prevu_ht": self.total_prevu_ht,
            "engage": self.engage,
            "realise": self.realise,
            "ecart": self.ecart,
        }


@dataclass
class DashboardFinancierDTO:
    """DTO principal du tableau de bord financier.

    FIN-11: Agrège les KPI, derniers achats et répartition par lot.
    """

    kpi: KPIFinancierDTO
    derniers_achats: List[DerniersAchatsDTO]
    repartition_par_lot: List[RepartitionLotDTO]

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "kpi": self.kpi.to_dict(),
            "derniers_achats": [a.to_dict() for a in self.derniers_achats],
            "repartition_par_lot": [
                r.to_dict() for r in self.repartition_par_lot
            ],
        }
