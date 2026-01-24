"""Schemas Pydantic pour les endpoints planning de charge."""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


# --- Schemas de requete ---


class CreateBesoinRequest(BaseModel):
    """Schema pour la creation d'un besoin de charge (PDC-16)."""

    chantier_id: int = Field(..., description="ID du chantier")
    semaine_code: str = Field(..., description="Code semaine (SXX-YYYY)", pattern=r"^S\d{2}-\d{4}$")
    type_metier: str = Field(..., description="Type de metier")
    besoin_heures: float = Field(..., ge=0, description="Nombre d'heures de besoin")
    note: Optional[str] = Field(None, description="Note optionnelle")


class UpdateBesoinRequest(BaseModel):
    """Schema pour la mise a jour d'un besoin."""

    besoin_heures: Optional[float] = Field(None, ge=0, description="Nouveau nombre d'heures")
    note: Optional[str] = Field(None, description="Nouvelle note")
    type_metier: Optional[str] = Field(None, description="Nouveau type de metier")


class PlanningChargeFiltersRequest(BaseModel):
    """Schema pour les filtres du planning de charge (PDC-03 a PDC-06)."""

    semaine_debut: str = Field(..., description="Semaine de debut (SXX-YYYY)")
    semaine_fin: str = Field(..., description="Semaine de fin (SXX-YYYY)")
    recherche: Optional[str] = Field(None, description="Recherche par nom de chantier (PDC-03)")
    mode_avance: bool = Field(False, description="Mode avance (PDC-04)")
    unite: str = Field("heures", description="Unite: heures ou jours_homme (PDC-05)")


# --- Schemas de reponse ---


class BesoinChargeResponse(BaseModel):
    """Schema de reponse pour un besoin de charge."""

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


class CelluleChargeResponse(BaseModel):
    """Schema pour une cellule du tableau (PDC-09)."""

    planifie_heures: float
    besoin_heures: float
    besoin_non_couvert: float
    has_besoin: bool
    est_couvert: bool


class SemaineChargeResponse(BaseModel):
    """Schema pour une semaine dans le planning (PDC-07)."""

    code: str
    label: str
    cellule: CelluleChargeResponse


class ChantierChargeResponse(BaseModel):
    """Schema pour un chantier dans le planning (PDC-01)."""

    id: int
    code: str
    nom: str
    couleur: str
    charge_totale: float  # PDC-08
    semaines: List[SemaineChargeResponse]


class FooterChargeResponse(BaseModel):
    """Schema pour le footer (PDC-11 a PDC-15)."""

    semaine_code: str
    taux_occupation: float  # PDC-12
    taux_couleur: str
    taux_label: str
    alerte_surcharge: bool  # PDC-13
    a_recruter: int  # PDC-14
    a_placer: int  # PDC-15


class PlanningChargeResponse(BaseModel):
    """Schema de reponse complete pour le planning de charge (PDC-01)."""

    total_chantiers: int  # PDC-02
    semaine_debut: str
    semaine_fin: str
    unite: str
    semaines: List[str]
    chantiers: List[ChantierChargeResponse]
    footer: List[FooterChargeResponse]
    capacite_totale: float
    planifie_total: float
    besoin_total: float


class TypeOccupationResponse(BaseModel):
    """Schema pour l'occupation par type (PDC-17)."""

    type_metier: str
    type_metier_label: str
    type_metier_couleur: str
    planifie_heures: float
    besoin_heures: float
    capacite_heures: float
    taux_occupation: float
    taux_couleur: str
    alerte: bool


class OccupationDetailsResponse(BaseModel):
    """Schema de reponse pour les details d'occupation (PDC-17)."""

    semaine_code: str
    semaine_label: str
    taux_global: float
    taux_global_couleur: str
    alerte_globale: bool
    types: List[TypeOccupationResponse]
    planifie_total: float
    besoin_total: float
    capacite_totale: float
    a_recruter: int
    a_placer: int


class ListeBesoinResponse(BaseModel):
    """Schema pour la liste des besoins."""

    items: List[BesoinChargeResponse]
    total: int
