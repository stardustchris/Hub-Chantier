"""Événement de domaine : Chantier mis à jour."""

from dataclasses import dataclass
from typing import Optional, Dict, Any

from shared.infrastructure.event_bus.domain_event import DomainEvent


@dataclass(frozen=True)
class ChantierUpdatedEvent(DomainEvent):
    """
    Événement : Chantier mis à jour.

    Cet événement est publié quand les détails d'un chantier sont modifiés.

    Attributes:
        chantier_id: ID unique du chantier.
        nom: Nom du chantier.
        adresse: Adresse du chantier.
        statut: Statut du chantier.
        changes: Dictionnaire des champs modifiés.
        metadata: Métadonnées additionnelles.

    Example:
        >>> event = ChantierUpdatedEvent(
        ...     chantier_id=1,
        ...     nom='Rénovation Rue de la Paix',
        ...     adresse='123 Rue de la Paix, 75000 Paris',
        ...     statut='en_cours',
        ...     changes={'statut': 'en_cours', 'nom': 'Rénovation Rue de la Paix'}
        ... )
    """

    def __init__(
        self,
        chantier_id: int,
        nom: str,
        adresse: str,
        statut: str,
        changes: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            event_type='chantier.updated',
            aggregate_id=str(chantier_id),
            data={
                'chantier_id': chantier_id,
                'nom': nom,
                'adresse': adresse,
                'statut': statut,
                'changes': changes
            },
            metadata=metadata or {}
        )
