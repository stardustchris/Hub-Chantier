"""Événement de domaine : Statut du chantier changé."""

from dataclasses import dataclass
from typing import Optional, Dict, Any

from shared.domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class ChantierStatutChangedEvent(DomainEvent):
    """
    Événement : Statut du chantier changé.

    Cet événement est publié quand le statut d'un chantier change
    (transitions: ouvert → en_cours → fermé).

    Attributes:
        chantier_id: ID unique du chantier.
        ancien_statut: Statut précédent (ouvert, en_cours, fermé).
        nouveau_statut: Nouveau statut (ouvert, en_cours, fermé).
        nom: Nom du chantier.
        adresse: Adresse du chantier.
        metadata: Métadonnées additionnelles (user_id, ip_address, etc).

    Example:
        >>> event = ChantierStatutChangedEvent(
        ...     chantier_id=1,
        ...     ancien_statut='ouvert',
        ...     nouveau_statut='en_cours',
        ...     nom='Rénovation Rue de la Paix',
        ...     adresse='123 Rue de la Paix, 75000 Paris'
        ... )
    """

    def __init__(
        self,
        chantier_id: int,
        ancien_statut: str,
        nouveau_statut: str,
        nom: str,
        adresse: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(
            event_type='chantier.statut_changed',
            aggregate_id=str(chantier_id),
            data={
                'chantier_id': chantier_id,
                'ancien_statut': ancien_statut,
                'nouveau_statut': nouveau_statut,
                'nom': nom,
                'adresse': adresse
            },
            metadata=metadata or {}
        )
