"""DTOs pour les debourses detailles.

DEV-05: Detail debourses avances.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.debourse_detail import DebourseDetail


@dataclass
class DebourseDetailCreateDTO:
    """DTO pour la creation d'un debourse detail."""

    type_debourse: str  # main_oeuvre, materiaux, sous_traitance, materiel, deplacement
    designation: str
    quantite: Decimal = Decimal("0")
    prix_unitaire: Decimal = Decimal("0")
    unite: str = "U"


@dataclass
class DebourseDetailDTO:
    """DTO de sortie pour un debourse detail."""

    id: int
    ligne_devis_id: int
    type_debourse: str
    designation: str
    quantite: str
    prix_unitaire: str
    montant: str
    unite: str

    @classmethod
    def from_entity(cls, debourse: DebourseDetail) -> DebourseDetailDTO:
        """Cree un DTO depuis une entite DebourseDetail."""
        return cls(
            id=debourse.id,
            ligne_devis_id=debourse.ligne_devis_id,
            type_debourse=debourse.type_debourse,
            designation=debourse.designation,
            quantite=str(debourse.quantite),
            prix_unitaire=str(debourse.prix_unitaire),
            montant=str(debourse.montant),
            unite=debourse.unite,
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "ligne_devis_id": self.ligne_devis_id,
            "type_debourse": self.type_debourse,
            "designation": self.designation,
            "quantite": self.quantite,
            "prix_unitaire": self.prix_unitaire,
            "montant": self.montant,
            "unite": self.unite,
        }
