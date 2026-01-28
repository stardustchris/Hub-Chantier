"""Classe de base pour les événements de domaine."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4


@dataclass(frozen=True)
class DomainEvent:
    """
    Classe de base pour tous les événements de domaine.

    Les événements sont immuables et représentent des faits qui se sont produits
    dans le système. Ils sont utilisés pour la communication entre modules (Event-Driven Architecture).

    Attributes:
        event_id: Identifiant unique de l'événement (UUID)
        event_type: Type d'événement au format '{module}.{action}' (ex: 'chantier.created')
        aggregate_id: ID de la ressource concernée (ex: chantier_id, user_id)
        data: Payload de l'événement (données métier)
        metadata: Métadonnées techniques (user_id, ip_address, user_agent, etc.)
        occurred_at: Timestamp UTC de création de l'événement

    Example:
        >>> event = DomainEvent(
        ...     event_type='chantier.created',
        ...     aggregate_id='123',
        ...     data={'nom': 'Nouveau chantier', 'adresse': '123 rue Test'},
        ...     metadata={'user_id': 1, 'user_email': 'admin@greg.fr'}
        ... )
    """

    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_type: str = ""
    aggregate_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    occurred_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """
        Sérialise l'événement en dictionnaire.

        Utilisé pour la persistance (event_logs) et les webhooks.

        Returns:
            dict: Représentation JSON-serializable de l'événement
        """
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'aggregate_id': self.aggregate_id,
            'data': self.data,
            'metadata': self.metadata,
            'occurred_at': self.occurred_at.isoformat()
        }

    def __str__(self) -> str:
        """Représentation string pour debugging."""
        return f"DomainEvent(type={self.event_type}, id={self.event_id}, aggregate={self.aggregate_id})"
