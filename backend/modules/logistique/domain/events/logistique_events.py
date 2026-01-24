"""Domain Events du module Logistique.

Ces events permettent de découpler les actions et déclencher
des side effects (notifications, logs, etc.).
"""

from dataclasses import dataclass, field
from datetime import datetime, date, time
from typing import Optional
import uuid


@dataclass(frozen=True)
class RessourceCreatedEvent:
    """Event émis lors de la création d'une ressource."""

    ressource_id: int
    nom: str
    code: str
    categorie: str
    created_by: int
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class RessourceUpdatedEvent:
    """Event émis lors de la modification d'une ressource."""

    ressource_id: int
    nom: str
    code: str
    updated_by: int
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class RessourceDeletedEvent:
    """Event émis lors de la suppression d'une ressource."""

    ressource_id: int
    deleted_by: int
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class ReservationCreatedEvent:
    """Event émis lors de la création d'une réservation.

    LOG-07: Demande de réservation
    LOG-13: Notification demande - Push au valideur
    """

    reservation_id: int
    ressource_id: int
    ressource_nom: str
    chantier_id: int
    demandeur_id: int
    date_reservation: date
    heure_debut: time
    heure_fin: time
    validation_requise: bool
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class ReservationValideeEvent:
    """Event émis lors de la validation d'une réservation.

    LOG-11: Workflow validation - Confirmée 🟢
    LOG-14: Notification décision - Push au demandeur
    """

    reservation_id: int
    ressource_id: int
    ressource_nom: str
    demandeur_id: int
    valideur_id: int
    date_reservation: date
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class ReservationRefuseeEvent:
    """Event émis lors du refus d'une réservation.

    LOG-14: Notification décision - Push au demandeur
    LOG-16: Motif de refus
    """

    reservation_id: int
    ressource_id: int
    ressource_nom: str
    demandeur_id: int
    valideur_id: int
    date_reservation: date
    motif: Optional[str] = None
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class ReservationAnnuleeEvent:
    """Event émis lors de l'annulation d'une réservation."""

    reservation_id: int
    ressource_id: int
    demandeur_id: int
    date_reservation: date
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class ReservationRappelEvent:
    """Event émis pour rappeler une réservation (J-1).

    LOG-15: Rappel J-1 - Notification veille de réservation
    """

    reservation_id: int
    ressource_id: int
    ressource_nom: str
    demandeur_id: int
    chantier_id: int
    date_reservation: date
    heure_debut: time
    heure_fin: time
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class ReservationConflitEvent:
    """Event émis lors de la détection d'un conflit.

    LOG-17: Conflit de réservation - Alerte si créneau déjà occupé
    """

    ressource_id: int
    date_reservation: date
    reservations_en_conflit: tuple  # IDs des réservations en conflit
    nouvelle_reservation_id: Optional[int] = None
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)
