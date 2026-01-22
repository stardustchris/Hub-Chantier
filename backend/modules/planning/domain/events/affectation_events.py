"""Événements de domaine pour les affectations."""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass(frozen=True)
class AffectationCreatedEvent:
    """
    Événement émis lors de la création d'une affectation.

    Selon CDC Section 5 - PLN-23: Notification push à chaque nouvelle affectation.

    Attributes:
        affectation_id: ID de l'affectation créée.
        utilisateur_id: ID de l'utilisateur affecté.
        chantier_id: ID du chantier d'affectation.
        date_affectation: Date de l'affectation.
        created_by: ID de l'utilisateur qui a créé l'affectation.
        timestamp: Date/heure de l'événement.
    """

    affectation_id: int
    utilisateur_id: int
    chantier_id: int
    date_affectation: date
    created_by: Optional[int] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Initialise le timestamp si non fourni."""
        if self.timestamp is None:
            object.__setattr__(self, "timestamp", datetime.now())


@dataclass(frozen=True)
class AffectationUpdatedEvent:
    """
    Événement émis lors de la modification d'une affectation.

    Attributes:
        affectation_id: ID de l'affectation modifiée.
        utilisateur_id: ID de l'utilisateur affecté.
        chantier_id: ID du chantier d'affectation.
        date_affectation: Nouvelle date de l'affectation.
        updated_by: ID de l'utilisateur qui a modifié.
        timestamp: Date/heure de l'événement.
    """

    affectation_id: int
    utilisateur_id: int
    chantier_id: int
    date_affectation: date
    updated_by: Optional[int] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Initialise le timestamp si non fourni."""
        if self.timestamp is None:
            object.__setattr__(self, "timestamp", datetime.now())


@dataclass(frozen=True)
class AffectationDeletedEvent:
    """
    Événement émis lors de la suppression d'une affectation.

    Attributes:
        affectation_id: ID de l'affectation supprimée.
        utilisateur_id: ID de l'utilisateur qui était affecté.
        chantier_id: ID du chantier concerné.
        date_affectation: Date de l'affectation supprimée.
        deleted_by: ID de l'utilisateur qui a supprimé.
        timestamp: Date/heure de l'événement.
    """

    affectation_id: int
    utilisateur_id: int
    chantier_id: int
    date_affectation: date
    deleted_by: Optional[int] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Initialise le timestamp si non fourni."""
        if self.timestamp is None:
            object.__setattr__(self, "timestamp", datetime.now())


@dataclass(frozen=True)
class AffectationsDupliquéesEvent:
    """
    Événement émis lors de la duplication d'affectations (PLN-16).

    Attributes:
        source_utilisateur_id: ID de l'utilisateur source.
        date_source_debut: Date de début de la période source.
        date_source_fin: Date de fin de la période source.
        date_cible_debut: Date de début de la période cible.
        nb_affectations: Nombre d'affectations dupliquées.
        created_by: ID de l'utilisateur qui a dupliqué.
        timestamp: Date/heure de l'événement.
    """

    source_utilisateur_id: int
    date_source_debut: date
    date_source_fin: date
    date_cible_debut: date
    nb_affectations: int
    created_by: Optional[int] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Initialise le timestamp si non fourni."""
        if self.timestamp is None:
            object.__setattr__(self, "timestamp", datetime.now())
