"""DTOs pour la decomposition des debourses.

DEV-05: Detail debourses avances - Vue decomposee par type de debourse.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DecomposeDebourseDTO:
    """DTO de sortie pour la decomposition des debourses d'une ligne.

    DEV-05: Breakdown par ligne : MOE, materiaux, sous-traitance, materiel, deplacement.
    """

    ligne_devis_id: int
    total_moe: str
    total_materiaux: str
    total_sous_traitance: str
    total_materiel: str
    total_deplacement: str
    debourse_sec: str
    details_par_type: Dict[str, List[dict]]

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "ligne_devis_id": self.ligne_devis_id,
            "total_moe": self.total_moe,
            "total_materiaux": self.total_materiaux,
            "total_sous_traitance": self.total_sous_traitance,
            "total_materiel": self.total_materiel,
            "total_deplacement": self.total_deplacement,
            "debourse_sec": self.debourse_sec,
            "details_par_type": self.details_par_type,
        }


@dataclass
class DecomposeLotDTO:
    """DTO de sortie pour la decomposition des debourses d'un lot.

    Aggrege les decompositions de toutes les lignes du lot.
    """

    lot_id: int
    lot_titre: str
    total_moe: str
    total_materiaux: str
    total_sous_traitance: str
    total_materiel: str
    total_deplacement: str
    debourse_sec: str
    lignes: List[DecomposeDebourseDTO]

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "lot_id": self.lot_id,
            "lot_titre": self.lot_titre,
            "total_moe": self.total_moe,
            "total_materiaux": self.total_materiaux,
            "total_sous_traitance": self.total_sous_traitance,
            "total_materiel": self.total_materiel,
            "total_deplacement": self.total_deplacement,
            "debourse_sec": self.debourse_sec,
            "lignes": [l.to_dict() for l in self.lignes],
        }


@dataclass
class DecomposeDevisDTO:
    """DTO de sortie pour la decomposition des debourses d'un devis complet.

    DEV-05: Vue interne uniquement - jamais visible sur le PDF client.
    """

    devis_id: int
    total_moe: str
    total_materiaux: str
    total_sous_traitance: str
    total_materiel: str
    total_deplacement: str
    debourse_sec_total: str
    lots: List[DecomposeLotDTO]

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "devis_id": self.devis_id,
            "total_moe": self.total_moe,
            "total_materiaux": self.total_materiaux,
            "total_sous_traitance": self.total_sous_traitance,
            "total_materiel": self.total_materiel,
            "total_deplacement": self.total_deplacement,
            "debourse_sec_total": self.debourse_sec_total,
            "lots": [lot.to_dict() for lot in self.lots],
        }
