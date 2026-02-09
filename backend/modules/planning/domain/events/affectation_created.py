"""Événement de domaine : Affectation créée."""

from dataclasses import dataclass
from datetime import date, time
from typing import Optional, Dict, Any

from shared.domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class AffectationCreatedEvent(DomainEvent):
    """
    Événement : Nouvelle affectation créée.

    Cet événement est publié quand un utilisateur est affecté à un chantier
    avec une date et des horaires optionnels.

    Attributes:
        affectation_id: ID unique de l'affectation créée.
        user_id: ID de l'utilisateur affecté.
        chantier_id: ID du chantier pour lequel l'affectation est créée.
        date_affectation: Date de l'affectation.
        heure_debut: Heure de début optionnelle.
        heure_fin: Heure de fin optionnelle.
        note: Notes optionnelles sur l'affectation.
        heures_prevues: Nombre d'heures prévues pour l'affectation (optionnel).
        metadata: Métadonnées additionnelles (user_id, ip_address, etc).

    Example:
        >>> event = AffectationCreatedEvent(
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
        heure_debut: Optional[time] = None,
        heure_fin: Optional[time] = None,
        note: Optional[str] = None,
        heures_prevues: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            event_type='affectation.created',
            aggregate_id=str(affectation_id),
            data={
                'affectation_id': affectation_id,
                'user_id': user_id,
                'chantier_id': chantier_id,
                'date': date_affectation.isoformat(),
                'heure_debut': heure_debut.isoformat() if heure_debut else None,
                'heure_fin': heure_fin.isoformat() if heure_fin else None,
                'note': note,
                'heures_prevues': heures_prevues
            },
            metadata=metadata or {}
        )
