"""Evenements du domaine Interventions.

Ces evenements permettent la communication inter-modules
sans couplage direct.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from ..value_objects import StatutIntervention, PrioriteIntervention, TypeIntervention


@dataclass(frozen=True)
class InterventionCreee:
    """Evenement emis lors de la creation d'une intervention."""

    intervention_id: int
    code: str
    type_intervention: TypeIntervention
    priorite: PrioriteIntervention
    client_nom: str
    created_by: int
    timestamp: datetime = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            object.__setattr__(self, "timestamp", datetime.utcnow())


@dataclass(frozen=True)
class InterventionPlanifiee:
    """Evenement emis lors de la planification d'une intervention."""

    intervention_id: int
    code: str
    date_planifiee: str  # ISO format
    heure_debut: Optional[str]
    heure_fin: Optional[str]
    techniciens_ids: List[int]
    timestamp: datetime = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            object.__setattr__(self, "timestamp", datetime.utcnow())


@dataclass(frozen=True)
class InterventionDemarree:
    """Evenement emis au demarrage d'une intervention."""

    intervention_id: int
    code: str
    technicien_id: int
    heure_debut_reelle: str
    timestamp: datetime = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            object.__setattr__(self, "timestamp", datetime.utcnow())


@dataclass(frozen=True)
class InterventionTerminee:
    """Evenement emis a la fin d'une intervention."""

    intervention_id: int
    code: str
    heure_fin_reelle: str
    travaux_realises: Optional[str]
    anomalies: Optional[str]
    timestamp: datetime = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            object.__setattr__(self, "timestamp", datetime.utcnow())


@dataclass(frozen=True)
class InterventionAnnulee:
    """Evenement emis a l'annulation d'une intervention."""

    intervention_id: int
    code: str
    annule_par: int
    timestamp: datetime = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            object.__setattr__(self, "timestamp", datetime.utcnow())


@dataclass(frozen=True)
class TechnicienAffecte:
    """Evenement emis lors de l'affectation d'un technicien."""

    intervention_id: int
    utilisateur_id: int
    est_principal: bool
    affecte_par: int
    timestamp: datetime = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            object.__setattr__(self, "timestamp", datetime.utcnow())


@dataclass(frozen=True)
class TechnicienDesaffecte:
    """Evenement emis lors de la desaffectation d'un technicien."""

    intervention_id: int
    utilisateur_id: int
    desaffecte_par: int
    timestamp: datetime = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            object.__setattr__(self, "timestamp", datetime.utcnow())


@dataclass(frozen=True)
class SignatureAjoutee:
    """Evenement emis lors de l'ajout d'une signature."""

    intervention_id: int
    type_signataire: str  # "client" ou "technicien"
    nom_signataire: str
    timestamp: datetime = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            object.__setattr__(self, "timestamp", datetime.utcnow())


@dataclass(frozen=True)
class RapportGenere:
    """Evenement emis lors de la generation du rapport PDF."""

    intervention_id: int
    code: str
    rapport_url: str
    genere_par: int
    timestamp: datetime = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            object.__setattr__(self, "timestamp", datetime.utcnow())


@dataclass(frozen=True)
class MessageAjoute:
    """Evenement emis lors de l'ajout d'un message."""

    intervention_id: int
    message_id: int
    type_message: str
    auteur_id: int
    timestamp: datetime = None

    def __post_init__(self) -> None:
        if self.timestamp is None:
            object.__setattr__(self, "timestamp", datetime.utcnow())
