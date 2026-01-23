"""DTOs pour les signalements."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class SignalementDTO:
    """DTO représentant un signalement."""

    id: int
    chantier_id: int
    titre: str
    description: str
    priorite: str
    priorite_label: str
    priorite_couleur: str
    statut: str
    statut_label: str
    statut_couleur: str
    cree_par: int
    cree_par_nom: Optional[str]
    assigne_a: Optional[int]
    assigne_a_nom: Optional[str]
    date_resolution_souhaitee: Optional[datetime]
    date_traitement: Optional[datetime]
    date_cloture: Optional[datetime]
    commentaire_traitement: Optional[str]
    photo_url: Optional[str]
    localisation: Optional[str]
    created_at: datetime
    updated_at: datetime
    est_en_retard: bool
    temps_restant: Optional[str]
    pourcentage_temps: float
    nb_reponses: int
    nb_escalades: int


@dataclass
class SignalementCreateDTO:
    """DTO pour la création d'un signalement."""

    chantier_id: int
    titre: str
    description: str
    cree_par: int
    priorite: str = "moyenne"
    assigne_a: Optional[int] = None
    date_resolution_souhaitee: Optional[datetime] = None
    photo_url: Optional[str] = None
    localisation: Optional[str] = None


@dataclass
class SignalementUpdateDTO:
    """DTO pour la mise à jour d'un signalement."""

    titre: Optional[str] = None
    description: Optional[str] = None
    priorite: Optional[str] = None
    assigne_a: Optional[int] = None
    date_resolution_souhaitee: Optional[datetime] = None
    photo_url: Optional[str] = None
    localisation: Optional[str] = None


@dataclass
class SignalementListDTO:
    """DTO pour la liste de signalements avec pagination."""

    signalements: List[SignalementDTO]
    total: int
    skip: int
    limit: int


@dataclass
class SignalementSearchDTO:
    """DTO pour la recherche de signalements (SIG-10, SIG-19, SIG-20)."""

    query: Optional[str] = None
    chantier_id: Optional[int] = None
    chantier_ids: Optional[List[int]] = None
    statut: Optional[str] = None
    priorite: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    cree_par: Optional[int] = None
    assigne_a: Optional[int] = None
    en_retard_only: bool = False
    skip: int = 0
    limit: int = 100


@dataclass
class SignalementStatsDTO:
    """DTO pour les statistiques des signalements (SIG-18)."""

    total: int
    par_statut: dict
    par_priorite: dict
    en_retard: int
    traites_cette_semaine: int
    temps_moyen_resolution: Optional[float]  # en heures
    taux_resolution: float  # pourcentage
