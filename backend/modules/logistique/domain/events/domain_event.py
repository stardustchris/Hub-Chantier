"""Base class pour les Domain Events."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass(frozen=True)
class DomainEvent:
    """Classe de base pour tous les événements de domaine.

    Attributes:
        event_id: Identifiant unique de l'événement.
        occurred_at: Date/heure à laquelle l'événement s'est produit.
    """

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_at: datetime = field(default_factory=datetime.utcnow)
