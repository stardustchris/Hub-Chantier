"""Événement de domaine : Document téléchargé."""

from dataclasses import dataclass
from typing import Optional, Dict, Any

from shared.domain.events.domain_event import DomainEvent


@dataclass(frozen=True)
class DocumentUploadedEvent(DomainEvent):
    """
    Événement : Nouveau document téléchargé.

    Cet événement est publié quand un document est téléchargé dans le système.

    Attributes:
        document_id: ID unique du document téléchargé.
        nom: Nom du fichier du document.
        type_document: Type de document (rapport, plan, facture, etc.).
        chantier_id: ID du chantier associé (optionnel).
        user_id: ID de l'utilisateur qui télécharge (optionnel).
        metadata: Métadonnées additionnelles (user_id, ip_address, etc).

    Example:
        >>> event = DocumentUploadedEvent(
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
            event_type='document.uploaded',
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
