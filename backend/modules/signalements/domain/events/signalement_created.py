"""Événement de domaine : Signalement créé."""

from dataclasses import dataclass
from typing import Optional, Dict, Any

from shared.infrastructure.event_bus.domain_event import DomainEvent


@dataclass(frozen=True)
class SignalementCreatedEvent(DomainEvent):
    """
    Événement : Nouveau signalement créé.

    Cet événement est publié quand un nouveau signalement (incident, problème, etc.)
    est créé sur un chantier.

    Attributes:
        signalement_id: ID unique du signalement créé.
        chantier_id: ID du chantier concerné.
        user_id: ID de l'utilisateur qui crée le signalement.
        titre: Titre/sujet du signalement.
        gravite: Niveau de gravité (basse, moyenne, haute, critique).
        metadata: Métadonnées additionnelles (user_id, ip_address, etc).

    Example:
        >>> event = SignalementCreatedEvent(
        ...     signalement_id=1,
        ...     chantier_id=10,
        ...     user_id=5,
        ...     titre='Équipement de sécurité manquant',
        ...     gravite='haute'
        ... )
    """

    def __init__(
        self,
        signalement_id: int,
        chantier_id: int,
        user_id: int,
        titre: str,
        gravite: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            event_type='signalement.created',
            aggregate_id=str(signalement_id),
            data={
                'signalement_id': signalement_id,
                'chantier_id': chantier_id,
                'user_id': user_id,
                'titre': titre,
                'gravite': gravite
            },
            metadata=metadata or {}
        )
