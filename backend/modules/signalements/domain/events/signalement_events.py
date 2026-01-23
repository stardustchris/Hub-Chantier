"""Événements de domaine pour les signalements."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class SignalementCreated:
    """Événement émis lors de la création d'un signalement."""

    signalement_id: int
    chantier_id: int
    titre: str
    priorite: str
    cree_par: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class SignalementUpdated:
    """Événement émis lors de la mise à jour d'un signalement."""

    signalement_id: int
    chantier_id: int
    updated_by: int
    changes: dict
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class SignalementAssigned:
    """Événement émis lors de l'assignation d'un signalement."""

    signalement_id: int
    chantier_id: int
    assigne_a: int
    assigned_by: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class SignalementStatusChanged:
    """Événement émis lors du changement de statut d'un signalement."""

    signalement_id: int
    chantier_id: int
    ancien_statut: str
    nouveau_statut: str
    changed_by: int
    commentaire: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class SignalementEscalated:
    """Événement émis lors de l'escalade d'un signalement (SIG-16, SIG-17)."""

    signalement_id: int
    chantier_id: int
    niveau_escalade: str  # "chef_chantier", "conducteur", "admin"
    pourcentage_temps: float
    destinataires: list
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass(frozen=True)
class ReponseAdded:
    """Événement émis lors de l'ajout d'une réponse."""

    reponse_id: int
    signalement_id: int
    auteur_id: int
    est_resolution: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
