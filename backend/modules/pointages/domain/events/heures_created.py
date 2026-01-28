"""Événement de domaine : Heures créées."""

from dataclasses import dataclass
from datetime import date
from typing import Optional, Dict, Any

from shared.infrastructure.event_bus.domain_event import DomainEvent


@dataclass(frozen=True)
class HeuresCreatedEvent(DomainEvent):
    """
    Événement : Nouvelles heures de travail créées.

    Cet événement est publié quand un enregistrement d'heures travaillées
    est créé pour un utilisateur sur un chantier.

    Attributes:
        heures_id: ID unique de l'enregistrement d'heures.
        user_id: ID de l'utilisateur.
        chantier_id: ID du chantier.
        date: Date des heures travaillées.
        heures_travaillees: Nombre d'heures travaillées.
        heures_supplementaires: Nombre d'heures supplémentaires (optionnel).
        metadata: Métadonnées additionnelles.

    Example:
        >>> event = HeuresCreatedEvent(
        ...     heures_id=1,
        ...     user_id=5,
        ...     chantier_id=10,
        ...     date=date(2026, 1, 28),
        ...     heures_travaillees=8.0,
        ...     heures_supplementaires=2.0
        ... )
    """

    def __init__(
        self,
        heures_id: int,
        user_id: int,
        chantier_id: int,
        date: date,
        heures_travaillees: float,
        heures_supplementaires: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            event_type='heures.created',
            aggregate_id=str(heures_id),
            data={
                'heures_id': heures_id,
                'user_id': user_id,
                'chantier_id': chantier_id,
                'date': date.isoformat(),
                'heures_travaillees': heures_travaillees,
                'heures_supplementaires': heures_supplementaires
            },
            metadata=metadata or {}
        )
