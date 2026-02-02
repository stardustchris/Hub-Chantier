"""DTOs pour les frais de chantier.

DEV-25: Frais de chantier - Compte prorata, frais generaux, installations.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ...domain.entities.frais_chantier_devis import FraisChantierDevis


@dataclass
class FraisChantierCreateDTO:
    """DTO pour la creation d'un frais de chantier."""

    devis_id: int
    type_frais: str
    libelle: str
    montant_ht: Decimal
    mode_repartition: str = "global"
    taux_tva: Decimal = Decimal("20")
    ordre: int = 0
    lot_devis_id: Optional[int] = None


@dataclass
class FraisChantierUpdateDTO:
    """DTO pour la mise a jour d'un frais de chantier."""

    type_frais: Optional[str] = None
    libelle: Optional[str] = None
    montant_ht: Optional[Decimal] = None
    mode_repartition: Optional[str] = None
    taux_tva: Optional[Decimal] = None
    ordre: Optional[int] = None
    lot_devis_id: Optional[int] = None


@dataclass
class FraisChantierDTO:
    """DTO de sortie pour un frais de chantier."""

    id: int
    devis_id: int
    type_frais: str
    libelle: str
    montant_ht: str
    montant_ttc: str
    mode_repartition: str
    taux_tva: str
    ordre: int
    lot_devis_id: Optional[int]

    @classmethod
    def from_entity(cls, frais: FraisChantierDevis) -> FraisChantierDTO:
        """Cree un DTO depuis une entite FraisChantierDevis.

        Args:
            frais: L'entite source.

        Returns:
            Le DTO correspondant.
        """
        return cls(
            id=frais.id,
            devis_id=frais.devis_id,
            type_frais=frais.type_frais.value,
            libelle=frais.libelle,
            montant_ht=str(frais.montant_ht),
            montant_ttc=str(frais.montant_ttc),
            mode_repartition=frais.mode_repartition.value,
            taux_tva=str(frais.taux_tva),
            ordre=frais.ordre,
            lot_devis_id=frais.lot_devis_id,
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "devis_id": self.devis_id,
            "type_frais": self.type_frais,
            "libelle": self.libelle,
            "montant_ht": self.montant_ht,
            "montant_ttc": self.montant_ttc,
            "mode_repartition": self.mode_repartition,
            "taux_tva": self.taux_tva,
            "ordre": self.ordre,
            "lot_devis_id": self.lot_devis_id,
        }
