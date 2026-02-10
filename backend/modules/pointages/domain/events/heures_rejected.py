"""Événement de domaine : Heures rejetées."""

from dataclasses import dataclass
from datetime import date
from typing import Optional, Dict, Any

from shared.domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class HeuresRejectedEvent(DomainEvent):
    """
    Événement : Heures de travail rejetées.

    Cet événement est publié quand un enregistrement d'heures est rejeté
    par un responsable, généralement pour des raisons de conformité ou d'erreur.

    Attributes:
        heures_id: ID unique de l'enregistrement d'heures.
        user_id: ID de l'utilisateur.
        chantier_id: ID du chantier.
        date: Date des heures rejetées.
        rejected_by: ID de l'utilisateur qui rejette.
        reason: Raison du rejet.
        metadata: Métadonnées additionnelles.

    Example:
        >>> event = HeuresRejectedEvent(
        ...     heures_id=1,
        ...     user_id=5,
        ...     chantier_id=10,
        ...     date=date(2026, 1, 28),
        ...     rejected_by=3,
        ...     reason='Incohérence avec planning'
        ... )
    """

    def __init__(
        self,
        heures_id: int,
        user_id: int,
        chantier_id: int,
        date: date,
        rejected_by: int,
        reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            event_type='heures.rejected',
            aggregate_id=str(heures_id),
            data={
                'heures_id': heures_id,
                'user_id': user_id,
                'chantier_id': chantier_id,
                'date': date.isoformat(),
                'rejected_by': rejected_by,
                'reason': reason
            },
            metadata=metadata or {}
        )
