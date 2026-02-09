"""Événement de domaine : Signalement mis à jour."""

from dataclasses import dataclass
from typing import Optional, Dict, Any

from shared.domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class SignalementUpdatedEvent(DomainEvent):
    """
    Événement : Signalement mis à jour.

    Cet événement est publié quand les détails d'un signalement sont modifiés.

    Attributes:
        signalement_id: ID unique du signalement.
        chantier_id: ID du chantier concerné.
        user_id: ID de l'utilisateur qui crée le signalement.
        titre: Titre/sujet du signalement.
        gravite: Niveau de gravité.
        changes: Dictionnaire des champs modifiés.
        metadata: Métadonnées additionnelles.

    Example:
        >>> event = SignalementUpdatedEvent(
        ...     signalement_id=1,
        ...     chantier_id=10,
        ...     user_id=5,
        ...     titre='Équipement de sécurité manquant',
        ...     gravite='critique',
        ...     changes={'gravite': 'critique'}
        ... )
    """

    def __init__(
        self,
        signalement_id: int,
        chantier_id: int,
        user_id: int,
        titre: str,
        gravite: str,
        changes: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            event_type='signalement.updated',
            aggregate_id=str(signalement_id),
            data={
                'signalement_id': signalement_id,
                'chantier_id': chantier_id,
                'user_id': user_id,
                'titre': titre,
                'gravite': gravite,
                'changes': changes
            },
            metadata=metadata or {}
        )
