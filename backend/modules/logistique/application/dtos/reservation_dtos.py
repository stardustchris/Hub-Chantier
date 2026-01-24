"""DTOs pour les réservations.

LOG-07 à LOG-18: Gestion des réservations et workflow.
"""

from dataclasses import dataclass, field
from datetime import datetime, date, time
from typing import Optional, List

from ...domain.value_objects import StatutReservation


@dataclass
class ReservationCreateDTO:
    """DTO pour la création d'une réservation.

    LOG-07: Demande de réservation
    LOG-08: Sélection chantier - Association obligatoire
    LOG-09: Sélection créneau - Date + heure début / heure fin
    """

    ressource_id: int
    chantier_id: int
    date_reservation: date
    heure_debut: time
    heure_fin: time
    commentaire: Optional[str] = None


@dataclass
class ReservationUpdateDTO:
    """DTO pour la mise à jour d'une réservation."""

    date_reservation: Optional[date] = None
    heure_debut: Optional[time] = None
    heure_fin: Optional[time] = None
    commentaire: Optional[str] = None


@dataclass
class ReservationDTO:
    """DTO de sortie pour une réservation.

    Inclut les informations enrichies (noms ressource, chantier, demandeur).
    """

    id: int
    ressource_id: int
    ressource_nom: Optional[str]
    ressource_code: Optional[str]
    ressource_couleur: Optional[str]
    chantier_id: int
    chantier_nom: Optional[str]
    demandeur_id: int
    demandeur_nom: Optional[str]
    date_reservation: date
    heure_debut: str
    heure_fin: str
    statut: str
    statut_label: str
    statut_couleur: str
    motif_refus: Optional[str]
    commentaire: Optional[str]
    valideur_id: Optional[int]
    valideur_nom: Optional[str]
    validated_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    @classmethod
    def from_entity(
        cls,
        reservation,
        ressource_nom: Optional[str] = None,
        ressource_code: Optional[str] = None,
        ressource_couleur: Optional[str] = None,
        chantier_nom: Optional[str] = None,
        demandeur_nom: Optional[str] = None,
        valideur_nom: Optional[str] = None,
    ) -> "ReservationDTO":
        """Crée un DTO depuis une entité Reservation."""
        return cls(
            id=reservation.id,
            ressource_id=reservation.ressource_id,
            ressource_nom=ressource_nom,
            ressource_code=ressource_code,
            ressource_couleur=ressource_couleur,
            chantier_id=reservation.chantier_id,
            chantier_nom=chantier_nom,
            demandeur_id=reservation.demandeur_id,
            demandeur_nom=demandeur_nom,
            date_reservation=reservation.date_reservation,
            heure_debut=reservation.heure_debut.isoformat(),
            heure_fin=reservation.heure_fin.isoformat(),
            statut=reservation.statut.value,
            statut_label=reservation.statut.label,
            statut_couleur=reservation.statut.couleur,
            motif_refus=reservation.motif_refus,
            commentaire=reservation.commentaire,
            valideur_id=reservation.valideur_id,
            valideur_nom=valideur_nom,
            validated_at=reservation.validated_at,
            created_at=reservation.created_at,
            updated_at=reservation.updated_at,
        )


@dataclass
class ReservationListDTO:
    """DTO pour une liste paginée de réservations."""

    items: List[ReservationDTO]
    total: int
    limit: int
    offset: int

    @property
    def has_more(self) -> bool:
        """Indique s'il y a plus de résultats."""
        return self.offset + len(self.items) < self.total


@dataclass
class PlanningRessourceDTO:
    """DTO pour le planning d'une ressource.

    LOG-03: Planning par ressource - Vue calendrier hebdomadaire 7 jours
    LOG-04: Navigation semaine
    """

    ressource_id: int
    ressource_nom: str
    ressource_code: str
    ressource_couleur: str
    date_debut: date
    date_fin: date
    reservations: List[ReservationDTO]
    jours: List[date] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Génère la liste des jours de la période."""
        if not self.jours:
            from datetime import timedelta

            current = self.date_debut
            self.jours = []
            while current <= self.date_fin:
                self.jours.append(current)
                current += timedelta(days=1)


@dataclass
class ReservationFiltersDTO:
    """DTO pour les filtres de recherche de réservations."""

    ressource_id: Optional[int] = None
    chantier_id: Optional[int] = None
    demandeur_id: Optional[int] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statuts: Optional[List[StatutReservation]] = None
    limit: int = 100
    offset: int = 0
