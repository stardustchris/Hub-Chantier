"""DTO pour les reponses d'affectation."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from ...domain.entities import Affectation


@dataclass(frozen=True)
class AffectationDTO:
    """
    Data Transfer Object pour une affectation (reponse).

    Utilise pour transferer les donnees d'affectation entre les couches.
    Inclut des champs optionnels d'enrichissement pour l'affichage UI.

    Selon CDC Section 5 - Planning Operationnel (PLN-01 a PLN-28).

    Attributes:
        id: Identifiant unique de l'affectation.
        utilisateur_id: ID de l'utilisateur affecte.
        chantier_id: ID du chantier.
        date: Date de l'affectation au format ISO.
        heures_prevues: Nombre d'heures prevues pour l'affectation (defaut: 8.0).
        heure_debut: Heure de debut au format "HH:MM" (optionnel).
        heure_fin: Heure de fin au format "HH:MM" (optionnel).
        note: Commentaire prive (optionnel).
        type_affectation: Type "unique" ou "recurrente".
        jours_recurrence: Jours de recurrence [0-6] (optionnel).
        created_at: Date de creation au format ISO.
        updated_at: Date de modification au format ISO.
        created_by: ID du createur.
        utilisateur_nom: Nom complet de l'utilisateur (enrichissement).
        utilisateur_couleur: Couleur de l'utilisateur (enrichissement).
        utilisateur_metier: Metier de l'utilisateur (enrichissement).
        chantier_nom: Nom du chantier (enrichissement).
        chantier_couleur: Couleur du chantier (enrichissement).

    Example:
        >>> dto = AffectationDTO.from_entity(affectation)
        >>> print(dto.date)
        '2026-01-22'
    """

    id: int
    utilisateur_id: int
    chantier_id: int
    date: str  # ISO format YYYY-MM-DD
    heures_prevues: float
    heure_debut: Optional[str]
    heure_fin: Optional[str]
    note: Optional[str]
    type_affectation: str
    jours_recurrence: Optional[List[int]]
    created_at: str  # ISO format
    updated_at: str  # ISO format
    created_by: int

    # Enrichissement optionnel (pour l'UI)
    utilisateur_nom: Optional[str] = None
    utilisateur_couleur: Optional[str] = None
    utilisateur_metier: Optional[str] = None
    utilisateur_role: Optional[str] = None
    utilisateur_type: Optional[str] = None
    chantier_nom: Optional[str] = None
    chantier_couleur: Optional[str] = None

    @staticmethod
    def from_entity(
        affectation: Affectation,
        utilisateur_nom: Optional[str] = None,
        utilisateur_couleur: Optional[str] = None,
        utilisateur_metier: Optional[str] = None,
        utilisateur_role: Optional[str] = None,
        utilisateur_type: Optional[str] = None,
        chantier_nom: Optional[str] = None,
        chantier_couleur: Optional[str] = None,
    ) -> "AffectationDTO":
        """
        Cree un DTO a partir d'une entite Affectation.

        Args:
            affectation: L'entite Affectation source.
            utilisateur_nom: Nom complet de l'utilisateur (optionnel).
            utilisateur_couleur: Couleur de l'utilisateur (optionnel).
            utilisateur_metier: Metier de l'utilisateur (optionnel).
            chantier_nom: Nom du chantier (optionnel).
            chantier_couleur: Couleur du chantier (optionnel).

        Returns:
            Le DTO correspondant avec enrichissements optionnels.

        Example:
            >>> dto = AffectationDTO.from_entity(
            ...     affectation,
            ...     utilisateur_nom="Jean Dupont",
            ...     chantier_nom="Chantier A"
            ... )
        """
        # Convertir les jours de recurrence en liste d'entiers
        jours_recurrence = None
        if affectation.jours_recurrence:
            jours_recurrence = [jour.value for jour in affectation.jours_recurrence]

        return AffectationDTO(
            id=affectation.id,
            utilisateur_id=affectation.utilisateur_id,
            chantier_id=affectation.chantier_id,
            date=affectation.date.isoformat(),
            heures_prevues=affectation.heures_prevues,
            heure_debut=str(affectation.heure_debut) if affectation.heure_debut else None,
            heure_fin=str(affectation.heure_fin) if affectation.heure_fin else None,
            note=affectation.note,
            type_affectation=affectation.type_affectation.value,
            jours_recurrence=jours_recurrence,
            created_at=_format_datetime(affectation.created_at),
            updated_at=_format_datetime(affectation.updated_at),
            created_by=affectation.created_by,
            utilisateur_nom=utilisateur_nom,
            utilisateur_couleur=utilisateur_couleur,
            utilisateur_metier=utilisateur_metier,
            utilisateur_role=utilisateur_role,
            utilisateur_type=utilisateur_type,
            chantier_nom=chantier_nom,
            chantier_couleur=chantier_couleur,
        )


@dataclass(frozen=True)
class AffectationListDTO:
    """
    DTO pour une liste paginee d'affectations.

    Attributes:
        affectations: Liste des affectations.
        total: Nombre total d'affectations.
        skip: Offset de pagination.
        limit: Limite de pagination.
    """

    affectations: List[AffectationDTO]
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


def _format_datetime(dt: datetime) -> str:
    """
    Formate un datetime en string ISO.

    Args:
        dt: Le datetime a formater.

    Returns:
        La chaine ISO correspondante.
    """
    return dt.isoformat() if dt else ""
