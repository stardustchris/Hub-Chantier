"""DTOs pour les affectations du module Planning."""

from dataclasses import dataclass, field
from datetime import date, time, datetime
from typing import Optional, List

from ...domain.entities import Affectation
from ...domain.value_objects import CreneauHoraire, TypeRecurrence


@dataclass
class CreateAffectationDTO:
    """
    DTO pour la création d'une affectation.

    Attributes:
        utilisateur_id: ID de l'utilisateur à affecter.
        chantier_id: ID du chantier d'affectation.
        date_affectation: Date de l'affectation (format ISO).
        heure_debut: Heure de début (format HH:MM, optionnel).
        heure_fin: Heure de fin (format HH:MM, optionnel).
        note: Commentaire privé (optionnel).
        recurrence: Type de récurrence (unique par défaut).
        jours_recurrence: Jours de répétition (0=lundi, 6=dimanche).
        date_fin_recurrence: Date de fin de récurrence (optionnel).
    """

    utilisateur_id: int
    chantier_id: int
    date_affectation: str  # ISO format: YYYY-MM-DD
    heure_debut: Optional[str] = None  # Format HH:MM
    heure_fin: Optional[str] = None  # Format HH:MM
    note: Optional[str] = None
    recurrence: str = "unique"
    jours_recurrence: List[int] = field(default_factory=list)
    date_fin_recurrence: Optional[str] = None


@dataclass
class UpdateAffectationDTO:
    """
    DTO pour la mise à jour d'une affectation.

    Tous les champs sont optionnels sauf l'ID.
    """

    affectation_id: int
    chantier_id: Optional[int] = None
    date_affectation: Optional[str] = None
    heure_debut: Optional[str] = None
    heure_fin: Optional[str] = None
    note: Optional[str] = None


@dataclass
class DeplacerAffectationDTO:
    """
    DTO pour déplacer une affectation (PLN-27: Drag & Drop).

    Attributes:
        affectation_id: ID de l'affectation à déplacer.
        nouvelle_date: Nouvelle date d'affectation.
        nouveau_chantier_id: Nouveau chantier (optionnel).
    """

    affectation_id: int
    nouvelle_date: str  # ISO format
    nouveau_chantier_id: Optional[int] = None


@dataclass
class DupliquerAffectationsDTO:
    """
    DTO pour dupliquer les affectations d'une période (PLN-16).

    Attributes:
        utilisateur_id: ID de l'utilisateur source.
        date_source_debut: Date de début de la période source.
        date_source_fin: Date de fin de la période source.
        date_cible_debut: Date de début de la période cible.
    """

    utilisateur_id: int
    date_source_debut: str
    date_source_fin: str
    date_cible_debut: str


@dataclass
class ListAffectationsDTO:
    """
    DTO pour lister les affectations avec filtres.

    Attributes:
        date_debut: Date de début de la période.
        date_fin: Date de fin de la période.
        utilisateur_id: Filtrer par utilisateur (optionnel).
        chantier_id: Filtrer par chantier (optionnel).
        skip: Offset pour pagination.
        limit: Limite pour pagination.
    """

    date_debut: str
    date_fin: str
    utilisateur_id: Optional[int] = None
    chantier_id: Optional[int] = None
    skip: int = 0
    limit: int = 100


@dataclass
class AffectationDTO:
    """
    DTO de sortie pour une affectation.

    Représentation complète d'une affectation pour l'API.
    """

    id: int
    utilisateur_id: int
    chantier_id: int
    date_affectation: str
    heure_debut: Optional[str]
    heure_fin: Optional[str]
    note: Optional[str]
    recurrence: str
    jours_recurrence: List[int]
    date_fin_recurrence: Optional[str]
    created_by: Optional[int]
    created_at: Optional[str]
    updated_at: Optional[str]

    @classmethod
    def from_entity(cls, affectation: Affectation) -> "AffectationDTO":
        """
        Crée un DTO depuis une entité Affectation.

        Args:
            affectation: L'entité à convertir.

        Returns:
            Le DTO correspondant.
        """
        heure_debut = None
        heure_fin = None
        if affectation.creneau:
            if affectation.creneau.heure_debut:
                heure_debut = affectation.creneau.heure_debut.strftime("%H:%M")
            if affectation.creneau.heure_fin:
                heure_fin = affectation.creneau.heure_fin.strftime("%H:%M")

        return cls(
            id=affectation.id,
            utilisateur_id=affectation.utilisateur_id,
            chantier_id=affectation.chantier_id,
            date_affectation=affectation.date_affectation.isoformat(),
            heure_debut=heure_debut,
            heure_fin=heure_fin,
            note=affectation.note,
            recurrence=affectation.recurrence.value,
            jours_recurrence=list(affectation.jours_recurrence),
            date_fin_recurrence=(
                affectation.date_fin_recurrence.isoformat()
                if affectation.date_fin_recurrence
                else None
            ),
            created_by=affectation.created_by,
            created_at=(
                affectation.created_at.isoformat() if affectation.created_at else None
            ),
            updated_at=(
                affectation.updated_at.isoformat() if affectation.updated_at else None
            ),
        )

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "id": self.id,
            "utilisateur_id": self.utilisateur_id,
            "chantier_id": self.chantier_id,
            "date_affectation": self.date_affectation,
            "heure_debut": self.heure_debut,
            "heure_fin": self.heure_fin,
            "note": self.note,
            "recurrence": self.recurrence,
            "jours_recurrence": self.jours_recurrence,
            "date_fin_recurrence": self.date_fin_recurrence,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class AffectationListDTO:
    """
    DTO de sortie pour une liste d'affectations paginée.

    Attributes:
        affectations: Liste des affectations.
        total: Nombre total d'éléments.
        skip: Offset utilisé.
        limit: Limite utilisée.
    """

    affectations: List[AffectationDTO]
    total: int
    skip: int
    limit: int

    def to_dict(self) -> dict:
        """Convertit le DTO en dictionnaire."""
        return {
            "affectations": [a.to_dict() for a in self.affectations],
            "total": self.total,
            "skip": self.skip,
            "limit": self.limit,
        }
