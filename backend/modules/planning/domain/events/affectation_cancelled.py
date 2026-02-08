"""Événement de domaine : Affectation annulée."""

from dataclasses import dataclass
from datetime import date
from typing import Optional, Dict, Any

from shared.domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class AffectationCancelledEvent(DomainEvent):
    """
    Événement : Affectation annulée.

    Cet événement est publié quand une affectation est annulée avant son exécution.
    Différent de 'deleted' qui est une suppression définitive.

    Attributes:
        affectation_id: ID unique de l'affectation annulée.
        user_id: ID de l'utilisateur concerné.
        chantier_id: ID du chantier.
        date_affectation: Date de l'affectation annulée.
        cancelled_by: ID de l'utilisateur qui annule.
        raison: Raison de l'annulation (optionnel).
        metadata: Métadonnées additionnelles.

    Example:
        >>> event = AffectationCancelledEvent(
        ...     affectation_id=42,
        ...     user_id=5,
        ...     chantier_id=10,
        ...     date_affectation=date(2026, 1, 30),
        ...     cancelled_by=3,
        ...     raison="Intempéries"
        ... )
        >>> event.event_type
        'affectation.cancelled'
    """

    def __init__(
        self,
        affectation_id: int,
        user_id: int,
        chantier_id: int,
        date_affectation: date,
        cancelled_by: int,
        raison: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            event_type='affectation.cancelled',
            aggregate_id=str(affectation_id),
            data={
                'affectation_id': affectation_id,
                'user_id': user_id,
                'chantier_id': chantier_id,
                'date_affectation': date_affectation.isoformat() if isinstance(date_affectation, date) else date_affectation,
                'cancelled_by': cancelled_by,
                'raison': raison
            },
            metadata=metadata or {}
        )
