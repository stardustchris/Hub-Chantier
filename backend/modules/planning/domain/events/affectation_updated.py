"""Événement de domaine : Affectation mise à jour."""

from dataclasses import dataclass
from datetime import date, time
from typing import Optional, Dict, Any

from shared.infrastructure.event_bus.domain_event import DomainEvent


@dataclass(frozen=True)
class AffectationUpdatedEvent(DomainEvent):
    """
    Événement : Affectation mise à jour.

    Cet événement est publié quand les détails d'une affectation sont modifiés.

    Attributes:
        affectation_id: ID unique de l'affectation mise à jour.
        user_id: ID de l'utilisateur affecté.
        chantier_id: ID du chantier.
        date_affectation: Date de l'affectation.
        heure_debut: Heure de début optionnelle.
        heure_fin: Heure de fin optionnelle.
        note: Notes optionnelles.
        changes: Dictionnaire des champs modifiés.
        metadata: Métadonnées additionnelles.

    Example:
        >>> event = AffectationUpdatedEvent(
        ...     affectation_id=1,
        ...     user_id=5,
        ...     chantier_id=10,
        ...     date_affectation=date(2026, 1, 28),
        ...     changes={'heure_debut': '08:00', 'heure_fin': '17:00'}
        ... )
    """

    def __init__(
        self,
        affectation_id: int,
        user_id: int,
        chantier_id: int,
        date_affectation: date,
        changes: Dict[str, Any],
        heure_debut: Optional[time] = None,
        heure_fin: Optional[time] = None,
        note: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            event_type='affectation.updated',
            aggregate_id=str(affectation_id),
            data={
                'affectation_id': affectation_id,
                'user_id': user_id,
                'chantier_id': chantier_id,
                'date': date_affectation.isoformat(),
                'heure_debut': heure_debut.isoformat() if heure_debut else None,
                'heure_fin': heure_fin.isoformat() if heure_fin else None,
                'note': note,
                'changes': changes
            },
            metadata=metadata or {}
        )
