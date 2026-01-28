"""Événement de domaine : Signalement fermé."""

from dataclasses import dataclass
from typing import Optional, Dict, Any

from shared.infrastructure.event_bus.domain_event import DomainEvent


@dataclass(frozen=True)
class SignalementClosedEvent(DomainEvent):
    """
    Événement : Signalement fermé.

    Cet événement est publié quand un signalement est fermé ou résolu.

    Attributes:
        signalement_id: ID unique du signalement fermé.
        chantier_id: ID du chantier concerné.
        user_id: ID de l'utilisateur qui a créé le signalement.
        titre: Titre/sujet du signalement.
        gravite: Niveau de gravité initial.
        closed_by: ID de l'utilisateur qui ferme le signalement.
        resolution: Description de la résolution.
        metadata: Métadonnées additionnelles.

    Example:
        >>> event = SignalementClosedEvent(
        ...     signalement_id=1,
        ...     chantier_id=10,
        ...     user_id=5,
        ...     titre='Équipement de sécurité manquant',
        ...     gravite='haute',
        ...     closed_by=3,
        ...     resolution='Équipement fourni et installé'
        ... )
    """

    def __init__(
        self,
        signalement_id: int,
        chantier_id: int,
        user_id: int,
        titre: str,
        gravite: str,
        closed_by: int,
        resolution: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            event_type='signalement.closed',
            aggregate_id=str(signalement_id),
            data={
                'signalement_id': signalement_id,
                'chantier_id': chantier_id,
                'user_id': user_id,
                'titre': titre,
                'gravite': gravite,
                'closed_by': closed_by,
                'resolution': resolution
            },
            metadata=metadata or {}
        )
