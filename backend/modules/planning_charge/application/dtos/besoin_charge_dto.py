"""DTOs pour les besoins de charge."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ...domain.entities import BesoinCharge
from ...domain.value_objects import Semaine, TypeMetier


@dataclass
class BesoinChargeDTO:
    """DTO representant un besoin de charge."""

    id: int
    chantier_id: int
    semaine_code: str
    semaine_label: str
    type_metier: str
    type_metier_label: str
    type_metier_couleur: str
    besoin_heures: float
    besoin_jours_homme: float
    note: Optional[str]
    created_by: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, besoin: BesoinCharge) -> "BesoinChargeDTO":
        """
        Cree un DTO a partir d'une entite.

        Args:
            besoin: L'entite BesoinCharge.

        Returns:
            Le DTO correspondant.
        """
        return cls(
            id=besoin.id,
            chantier_id=besoin.chantier_id,
            semaine_code=besoin.semaine.code,
            semaine_label=str(besoin.semaine),
            type_metier=besoin.type_metier.value,
            type_metier_label=besoin.type_metier.label,
            type_metier_couleur=besoin.type_metier.couleur,
            besoin_heures=besoin.besoin_heures,
            besoin_jours_homme=besoin.besoin_jours_homme,
            note=besoin.note,
            created_by=besoin.created_by,
            created_at=besoin.created_at,
            updated_at=besoin.updated_at,
        )


@dataclass
class CreateBesoinDTO:
    """DTO pour la creation d'un besoin de charge."""

    chantier_id: int
    semaine_code: str  # Format SXX-YYYY
    type_metier: str
    besoin_heures: float
    note: Optional[str] = None

    def to_entity(self, created_by: int) -> BesoinCharge:
        """
        Convertit le DTO en entite.

        Args:
            created_by: ID de l'utilisateur createur.

        Returns:
            L'entite BesoinCharge.
        """
        return BesoinCharge(
            chantier_id=self.chantier_id,
            semaine=Semaine.from_code(self.semaine_code),
            type_metier=TypeMetier.from_string(self.type_metier),
            besoin_heures=self.besoin_heures,
            note=self.note,
            created_by=created_by,
        )


@dataclass
class UpdateBesoinDTO:
    """DTO pour la mise a jour d'un besoin de charge."""

    besoin_heures: Optional[float] = None
    note: Optional[str] = None
    type_metier: Optional[str] = None
