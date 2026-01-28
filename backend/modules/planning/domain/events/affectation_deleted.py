"""Événement de domaine : Affectation supprimée."""

from dataclasses import dataclass
from datetime import date
from typing import Optional, Dict, Any

from shared.infrastructure.event_bus.domain_event import DomainEvent


@dataclass(frozen=True)
class AffectationDeletedEvent(DomainEvent):
    """
    Événement : Affectation supprimée.

    Cet événement est publié quand une affectation est supprimée du système.

    Attributes:
        affectation_id: ID unique de l'affectation supprimée.
        user_id: ID de l'utilisateur affecté.
        chantier_id: ID du chantier.
        date_affectation: Date de l'affectation supprimée.
        metadata: Métadonnées additionnelles (user_id, ip_address, etc).

    Example:
        >>> event = AffectationDeletedEvent(
        ...     affectation_id=1,
        ...     user_id=5,
        ...     chantier_id=10,
        ...     date_affectation=date(2026, 1, 28)
        ... )
    """

    def __init__(
        self,
        affectation_id: int,
        user_id: int,
        chantier_id: int,
        date_affectation: date,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            event_type='affectation.deleted',
            aggregate_id=str(affectation_id),
            data={
                'affectation_id': affectation_id,
                'user_id': user_id,
                'chantier_id': chantier_id,
                'date': date_affectation.isoformat()
            },
            metadata=metadata or {}
        )
