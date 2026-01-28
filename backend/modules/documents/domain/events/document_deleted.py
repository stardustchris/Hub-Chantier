"""Événement de domaine : Document supprimé."""

from dataclasses import dataclass
from typing import Optional, Dict, Any

from shared.infrastructure.event_bus.domain_event import DomainEvent


@dataclass(frozen=True)
class DocumentDeletedEvent(DomainEvent):
    """
    Événement : Document supprimé.

    Cet événement est publié quand un document est supprimé du système.

    Attributes:
        document_id: ID unique du document supprimé.
        nom: Nom du fichier du document supprimé.
        type_document: Type de document.
        chantier_id: ID du chantier associé (optionnel).
        user_id: ID de l'utilisateur qui a téléchargé (optionnel).
        metadata: Métadonnées additionnelles (user_id, ip_address, etc).

    Example:
        >>> event = DocumentDeletedEvent(
        ...     document_id=1,
        ...     nom='plans_architecture.pdf',
        ...     type_document='plan',
        ...     chantier_id=10,
        ...     user_id=5
        ... )
    """

    def __init__(
        self,
        document_id: int,
        nom: str,
        type_document: str,
        chantier_id: Optional[int] = None,
        user_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            event_type='document.deleted',
            aggregate_id=str(document_id),
            data={
                'document_id': document_id,
                'nom': nom,
                'type_document': type_document,
                'chantier_id': chantier_id,
                'user_id': user_id
            },
            metadata=metadata or {}
        )
