"""Événement de domaine : Heures mises à jour."""

from dataclasses import dataclass
from datetime import date
from typing import Optional, Dict, Any

from shared.domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class HeuresUpdatedEvent(DomainEvent):
    """
    Événement : Heures de travail mises à jour.

    Cet événement est publié quand un enregistrement d'heures est modifié.

    Attributes:
        heures_id: ID unique de l'enregistrement d'heures.
        user_id: ID de l'utilisateur.
        chantier_id: ID du chantier.
        date: Date des heures travaillées.
        heures_travaillees: Nombre d'heures travaillées.
        heures_supplementaires: Nombre d'heures supplémentaires.
        changes: Dictionnaire des champs modifiés.
        metadata: Métadonnées additionnelles.

    Example:
        >>> event = HeuresUpdatedEvent(
        ...     heures_id=1,
        ...     user_id=5,
        ...     chantier_id=10,
        ...     date=date(2026, 1, 28),
        ...     heures_travaillees=8.5,
        ...     heures_supplementaires=1.5,
        ...     changes={'heures_travaillees': 8.5}
        ... )
    """

    def __init__(
        self,
        heures_id: int,
        user_id: int,
        chantier_id: int,
        date: date,
        heures_travaillees: float,
        heures_supplementaires: float,
        changes: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            event_type='heures.updated',
            aggregate_id=str(heures_id),
            data={
                'heures_id': heures_id,
                'user_id': user_id,
                'chantier_id': chantier_id,
                'date': date.isoformat(),
                'heures_travaillees': heures_travaillees,
                'heures_supplementaires': heures_supplementaires,
                'changes': changes
            },
            metadata=metadata or {}
        )
