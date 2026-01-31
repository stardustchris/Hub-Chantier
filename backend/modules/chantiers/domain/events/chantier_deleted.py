"""Événement de domaine : Chantier supprimé."""

from dataclasses import dataclass
from typing import Optional, Dict, Any

from shared.infrastructure.event_bus.domain_event import DomainEvent


@dataclass(frozen=True)
class ChantierDeletedEvent(DomainEvent):
    """
    Événement : Chantier supprimé.

    Cet événement est publié quand un chantier est supprimé du système.

    Attributes:
        chantier_id: ID unique du chantier supprimé.
        nom: Nom du chantier supprimé.
        adresse: Adresse du chantier supprimé.
        metadata: Métadonnées additionnelles (user_id, ip_address, etc).

    Example:
        >>> event = ChantierDeletedEvent(
        ...     chantier_id=1,
        ...     nom='Rénovation Rue de la Paix',
        ...     adresse='123 Rue de la Paix, 75000 Paris'
        ... )
    """

    def __init__(
        self,
        chantier_id: int,
        nom: str,
        adresse: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            event_type='chantier.deleted',
            aggregate_id=str(chantier_id),
            data={
                'chantier_id': chantier_id,
                'nom': nom,
                'adresse': adresse
            },
            metadata=metadata or {}
        )
