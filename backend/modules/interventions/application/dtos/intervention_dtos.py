"""DTOs pour le module Interventions."""

from datetime import date, time, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

from ...domain.value_objects import (
    StatutIntervention,
    PrioriteIntervention,
    TypeIntervention,
)


class CreateInterventionDTO(BaseModel):
    """DTO pour la creation d'une intervention.

    INT-03: Creation intervention
    INT-04: Fiche intervention
    """

    type_intervention: TypeIntervention
    priorite: PrioriteIntervention = PrioriteIntervention.NORMALE
    client_nom: str = Field(..., min_length=1, max_length=200)
    client_adresse: str = Field(..., min_length=1)
    client_telephone: Optional[str] = Field(None, max_length=20)
    client_email: Optional[str] = Field(None, max_length=200)
    description: str = Field(..., min_length=1)
    date_souhaitee: Optional[date] = None
    chantier_origine_id: Optional[int] = None

    @field_validator("client_nom", "client_adresse", "description")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return v.strip() if v else v


class UpdateInterventionDTO(BaseModel):
    """DTO pour la mise a jour d'une intervention."""

    type_intervention: Optional[TypeIntervention] = None
    priorite: Optional[PrioriteIntervention] = None
    client_nom: Optional[str] = Field(None, min_length=1, max_length=200)
    client_adresse: Optional[str] = Field(None, min_length=1)
    client_telephone: Optional[str] = Field(None, max_length=20)
    client_email: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, min_length=1)
    date_souhaitee: Optional[date] = None
    travaux_realises: Optional[str] = None
    anomalies: Optional[str] = None


class PlanifierInterventionDTO(BaseModel):
    """DTO pour planifier une intervention.

    INT-05: Statuts intervention (passage a PLANIFIEE)
    INT-06: Planning hebdomadaire
    """

    date_planifiee: date
    heure_debut: Optional[time] = None
    heure_fin: Optional[time] = None
    techniciens_ids: List[int] = Field(default_factory=list)

    @field_validator("heure_fin")
    @classmethod
    def validate_heure_fin(cls, v, info):
        heure_debut = info.data.get("heure_debut")
        if v and heure_debut and v <= heure_debut:
            raise ValueError("L'heure de fin doit etre posterieure a l'heure de debut")
        return v


class DemarrerInterventionDTO(BaseModel):
    """DTO pour demarrer une intervention."""

    heure_debut_reelle: Optional[time] = None


class TerminerInterventionDTO(BaseModel):
    """DTO pour terminer une intervention."""

    heure_fin_reelle: Optional[time] = None
    travaux_realises: Optional[str] = None
    anomalies: Optional[str] = None


class InterventionResponseDTO(BaseModel):
    """DTO de reponse pour une intervention.

    INT-02: Liste des interventions
    """

    id: int
    code: str
    type_intervention: TypeIntervention
    statut: StatutIntervention
    priorite: PrioriteIntervention
    client_nom: str
    client_adresse: str
    client_telephone: Optional[str]
    client_email: Optional[str]
    description: str
    travaux_realises: Optional[str]
    anomalies: Optional[str]
    date_souhaitee: Optional[date]
    date_planifiee: Optional[date]
    heure_debut: Optional[time]
    heure_fin: Optional[time]
    heure_debut_reelle: Optional[time]
    heure_fin_reelle: Optional[time]
    chantier_origine_id: Optional[int]
    rapport_genere: bool
    rapport_url: Optional[str]
    created_by: int
    created_at: datetime
    updated_at: datetime

    # Enrichissement
    techniciens: Optional[List["TechnicienResponseDTO"]] = None
    nb_messages: Optional[int] = None
    has_signature_client: Optional[bool] = None

    model_config = {"from_attributes": True}


class InterventionListResponseDTO(BaseModel):
    """DTO pour une liste paginee d'interventions."""

    items: List[InterventionResponseDTO]
    total: int
    limit: int
    offset: int


class InterventionFiltersDTO(BaseModel):
    """DTO pour les filtres de recherche."""

    statut: Optional[StatutIntervention] = None
    priorite: Optional[PrioriteIntervention] = None
    type_intervention: Optional[TypeIntervention] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    chantier_origine_id: Optional[int] = None
    limit: int = Field(100, ge=1, le=500)
    offset: int = Field(0, ge=0)


class TechnicienResponseDTO(BaseModel):
    """DTO pour un technicien affecte."""

    id: int
    utilisateur_id: int
    nom: Optional[str] = None
    prenom: Optional[str] = None
    est_principal: bool
    commentaire: Optional[str]

    model_config = {"from_attributes": True}


class AffecterTechnicienDTO(BaseModel):
    """DTO pour affecter un technicien.

    INT-10: Affectation technicien
    INT-17: Affectation sous-traitants
    """

    utilisateur_id: int
    est_principal: bool = False
    commentaire: Optional[str] = None


class MessageResponseDTO(BaseModel):
    """DTO pour un message d'intervention.

    INT-11: Fil d'actualite
    INT-12: Chat intervention
    """

    id: int
    intervention_id: int
    auteur_id: int
    auteur_nom: Optional[str] = None
    type_message: str
    contenu: str
    photos_urls: List[str]
    inclure_rapport: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CreateMessageDTO(BaseModel):
    """DTO pour creer un message."""

    type_message: str = "commentaire"
    contenu: str = Field(..., min_length=1)
    photos_urls: List[str] = Field(default_factory=list)


class SignatureResponseDTO(BaseModel):
    """DTO pour une signature.

    INT-13: Signature client
    INT-14: Signatures dans rapport PDF
    """

    id: int
    intervention_id: int
    type_signataire: str
    nom_signataire: str
    utilisateur_id: Optional[int]
    signed_at: datetime
    horodatage_str: str

    model_config = {"from_attributes": True}


class CreateSignatureDTO(BaseModel):
    """DTO pour creer une signature."""

    type_signataire: str  # "client" ou "technicien"
    nom_signataire: str = Field(..., min_length=1, max_length=200)
    signature_data: str = Field(..., min_length=1)
    latitude: Optional[float] = None
    longitude: Optional[float] = None


# Forward reference update
InterventionResponseDTO.model_rebuild()
