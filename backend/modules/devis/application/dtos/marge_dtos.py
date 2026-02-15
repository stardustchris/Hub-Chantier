"""DTOs pour la gestion des marges et coefficients.

DEV-06: Gestion marges et coefficients.
Application marges globales / par lot / par ligne.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional


@dataclass
class AppliquerMargeGlobaleDTO:
    """DTO pour appliquer une marge globale a un devis.

    DEV-06: Marge au niveau global (priorite 4).
    """

    devis_id: int
    taux_marge_global: Decimal
    coefficient_frais_generaux: Optional[Decimal] = None
    # Marges par type de debourse (priorite 3)
    taux_marge_moe: Optional[Decimal] = None
    taux_marge_materiaux: Optional[Decimal] = None
    taux_marge_sous_traitance: Optional[Decimal] = None
    taux_marge_materiel: Optional[Decimal] = None
    taux_marge_deplacement: Optional[Decimal] = None


@dataclass
class AppliquerMargeLotDTO:
    """DTO pour appliquer une marge sur un lot.

    DEV-06: Marge au niveau lot (priorite 2).
    """

    lot_id: int
    taux_marge_lot: Optional[Decimal]  # None = utilise la marge parente


@dataclass
class AppliquerMargeLigneDTO:
    """DTO pour appliquer une marge sur une ligne.

    DEV-06: Marge au niveau ligne (priorite 1).
    """

    ligne_id: int
    taux_marge_ligne: Optional[Decimal]  # None = utilise la marge parente


@dataclass
class MargeResolueDTO:
    """DTO de sortie pour la marge resolue d'une ligne.

    Indique le taux effectif et le niveau de la hierarchie
    qui a fourni cette marge.
    """

    ligne_id: int
    taux_marge: str
    niveau: str  # "ligne", "lot", "type_debourse", "global"
    debourse_sec: str
    prix_revient: str
    prix_vente_ht: str

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "ligne_id": self.ligne_id,
            "taux_marge": self.taux_marge,
            "niveau": self.niveau,
            "debourse_sec": self.debourse_sec,
            "prix_revient": self.prix_revient,
            "prix_vente_ht": self.prix_vente_ht,
        }


@dataclass
class MargesDevisDTO:
    """DTO de sortie pour le resume des marges d'un devis.

    DEV-06: Vue Debours (interne uniquement).
    """

    devis_id: int
    taux_marge_global: str
    coefficient_frais_generaux: str
    taux_marge_moe: Optional[str]
    taux_marge_materiaux: Optional[str]
    taux_marge_sous_traitance: Optional[str]
    taux_marge_materiel: Optional[str]
    taux_marge_deplacement: Optional[str]
    total_debourse_sec: str
    total_prix_revient: str
    total_prix_vente_ht: str
    marge_globale_montant: str
    lignes: List[MargeResolueDTO]

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "devis_id": self.devis_id,
            "taux_marge_global": self.taux_marge_global,
            "coefficient_frais_generaux": self.coefficient_frais_generaux,
            "taux_marge_moe": self.taux_marge_moe,
            "taux_marge_materiaux": self.taux_marge_materiaux,
            "taux_marge_sous_traitance": self.taux_marge_sous_traitance,
            "taux_marge_materiel": self.taux_marge_materiel,
            "taux_marge_deplacement": self.taux_marge_deplacement,
            "total_debourse_sec": self.total_debourse_sec,
            "total_prix_revient": self.total_prix_revient,
            "total_prix_vente_ht": self.total_prix_vente_ht,
            "marge_globale_montant": self.marge_globale_montant,
            "lignes": [l.to_dict() for l in self.lignes],
        }
