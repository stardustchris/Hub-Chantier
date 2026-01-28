"""Événement de domaine : Heures validées."""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional, Dict, Any

from shared.infrastructure.event_bus.domain_event import DomainEvent


@dataclass(frozen=True)
class HeuresValidatedEvent(DomainEvent):
    """
    Événement : Heures de travail validées.

    ⚠️ CRITIQUE pour la synchronisation avec le système de paie.

    Cet événement est publié quand un enregistrement d'heures est officiellement
    validé par un responsable. C'est un événement critique qui déclenche
    la synchronisation avec le système de gestion de la paie.

    Attributes:
        heures_id: ID unique de l'enregistrement d'heures.
        user_id: ID de l'utilisateur.
        chantier_id: ID du chantier.
        date: Date des heures validées.
        heures_travaillees: Nombre d'heures validées.
        heures_supplementaires: Nombre d'heures supplémentaires validées.
        validated_by: ID de l'utilisateur qui valide.
        validated_at: Timestamp de validation.
        metadata: Métadonnées additionnelles.

    Example:
        >>> event = HeuresValidatedEvent(
        ...     heures_id=1,
        ...     user_id=5,
        ...     chantier_id=10,
        ...     date=date(2026, 1, 28),
        ...     heures_travaillees=8.0,
        ...     heures_supplementaires=2.0,
        ...     validated_by=3
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
        validated_by: int,
        validated_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            event_type='heures.validated',
            aggregate_id=str(heures_id),
            data={
                'heures_id': heures_id,
                'user_id': user_id,
                'chantier_id': chantier_id,
                'date': date.isoformat(),
                'heures_travaillees': heures_travaillees,
                'heures_supplementaires': heures_supplementaires,
                'validated_by': validated_by,
                'validated_at': validated_at.isoformat() if validated_at else None
            },
            metadata=metadata or {}
        )
