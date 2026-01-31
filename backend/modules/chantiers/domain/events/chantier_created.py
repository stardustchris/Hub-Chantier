"""Événement de domaine : Chantier créé."""

from dataclasses import dataclass
from typing import Optional, Dict, Any

from shared.infrastructure.event_bus.domain_event import DomainEvent


@dataclass(frozen=True)
class ChantierCreatedEvent(DomainEvent):
    """
    Événement : Nouveau chantier créé.

    Cet événement est publié quand un nouveau chantier est créé dans le système.

    Attributes:
        chantier_id: ID unique du chantier créé.
        nom: Nom du chantier.
        adresse: Adresse du chantier.
        statut: Statut initial du chantier (ouvert, en_cours, fermé).
        metadata: Métadonnées additionnelles (user_id, ip_address, etc).

    Example:
        >>> event = ChantierCreatedEvent(
        ...     chantier_id=1,
        ...     nom='Rénovation Rue de la Paix',
        ...     adresse='123 Rue de la Paix, 75000 Paris',
        ...     statut='ouvert'
        ... )
    """

    def __init__(
        self,
        chantier_id: int,
        nom: str,
        adresse: str,
        statut: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            event_type='chantier.created',
            aggregate_id=str(chantier_id),
            data={
                'chantier_id': chantier_id,
                'nom': nom,
                'adresse': adresse,
                'statut': statut
            },
            metadata=metadata or {}
        )
