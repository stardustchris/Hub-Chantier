"""DTOs pour les reservations.

CDC Section 11 - LOG-07 a LOG-18.
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional, List

from ...domain.entities import Reservation


@dataclass(frozen=True)
class CreateReservationDTO:
    """DTO pour la creation d'une reservation (LOG-07)."""
    ressource_id: int
    chantier_id: int  # Obligatoire (LOG-08)
    demandeur_id: int
    date_debut: date  # LOG-09
    date_fin: date
    heure_debut: str
    heure_fin: str
    note: Optional[str] = None


@dataclass(frozen=True)
class ValidateReservationDTO:
    """DTO pour valider une reservation (LOG-11)."""
    reservation_id: int
    valideur_id: int


@dataclass(frozen=True)
class RefuseReservationDTO:
    """DTO pour refuser une reservation (LOG-11, LOG-16)."""
    reservation_id: int
    valideur_id: int
    motif: Optional[str] = None  # LOG-16


@dataclass(frozen=True)
class ReservationFiltersDTO:
    """DTO pour les filtres de recherche de reservations."""
    ressource_id: Optional[int] = None
    chantier_id: Optional[int] = None
    demandeur_id: Optional[int] = None
    statut: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    skip: int = 0
    limit: int = 50


@dataclass(frozen=True)
class ReservationDTO:
    """DTO de reponse pour une reservation."""
    id: int
    ressource_id: int
    chantier_id: int
    demandeur_id: int
    valideur_id: Optional[int]
    date_debut: str
    date_fin: str
    heure_debut: str
    heure_fin: str
    statut: str
    statut_label: str
    statut_couleur: str
    motif_refus: Optional[str]
    note: Optional[str]
    validated_at: Optional[str]
    refused_at: Optional[str]
    cancelled_at: Optional[str]
    created_at: str
    updated_at: str
    # Enrichissement (optionnel)
    ressource_nom: Optional[str] = None
    ressource_couleur: Optional[str] = None
    chantier_nom: Optional[str] = None
    demandeur_nom: Optional[str] = None
    valideur_nom: Optional[str] = None

    @staticmethod
    def from_entity(
        reservation: Reservation,
        ressource_nom: Optional[str] = None,
        ressource_couleur: Optional[str] = None,
        chantier_nom: Optional[str] = None,
        demandeur_nom: Optional[str] = None,
        valideur_nom: Optional[str] = None,
    ) -> "ReservationDTO":
        """Convertit une entite en DTO avec enrichissement optionnel."""
        return ReservationDTO(
            id=reservation.id,  # type: ignore
            ressource_id=reservation.ressource_id,
            chantier_id=reservation.chantier_id,
            demandeur_id=reservation.demandeur_id,
            valideur_id=reservation.valideur_id,
            date_debut=reservation.date_debut.isoformat(),
            date_fin=reservation.date_fin.isoformat(),
            heure_debut=reservation.heure_debut,
            heure_fin=reservation.heure_fin,
            statut=reservation.statut.value,
            statut_label=reservation.statut.label,
            statut_couleur=reservation.statut.couleur,
            motif_refus=reservation.motif_refus,
            note=reservation.note,
            validated_at=reservation.validated_at.isoformat() if reservation.validated_at else None,
            refused_at=reservation.refused_at.isoformat() if reservation.refused_at else None,
            cancelled_at=reservation.cancelled_at.isoformat() if reservation.cancelled_at else None,
            created_at=reservation.created_at.isoformat(),
            updated_at=reservation.updated_at.isoformat(),
            ressource_nom=ressource_nom,
            ressource_couleur=ressource_couleur,
            chantier_nom=chantier_nom,
            demandeur_nom=demandeur_nom,
            valideur_nom=valideur_nom,
        )


@dataclass(frozen=True)
class ReservationListDTO:
    """DTO pour une liste paginee de reservations."""
    reservations: List[ReservationDTO]
    total: int
    skip: int
    limit: int

    @property
    def has_next(self) -> bool:
        """Indique s'il y a une page suivante."""
        return self.skip + self.limit < self.total

    @property
    def has_previous(self) -> bool:
        """Indique s'il y a une page precedente."""
        return self.skip > 0


@dataclass(frozen=True)
class PlanningRessourceDTO:
    """DTO pour le planning d'une ressource sur une semaine (LOG-03)."""
    ressource: "RessourceDTO"
    reservations: List[ReservationDTO]
    semaine_debut: str  # YYYY-MM-DD (lundi)
    semaine_fin: str    # YYYY-MM-DD (dimanche)


@dataclass(frozen=True)
class ConflitReservationDTO:
    """DTO pour signaler un conflit de reservation (LOG-17)."""
    nouvelle_reservation: CreateReservationDTO
    reservations_en_conflit: List[ReservationDTO]
    message: str


# Import pour eviter import circulaire
from .ressource_dto import RessourceDTO  # noqa: E402
