"""DTOs pour le module Audit."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Any
from uuid import UUID

from ...domain.entities.audit_entry import AuditEntry


@dataclass
class LogAuditEntryDTO:
    """
    DTO pour enregistrer une nouvelle entrée d'audit.

    Utilisé par le service applicatif pour créer des entrées d'audit.
    """

    entity_type: str
    entity_id: str
    action: str
    author_id: int
    field_name: Optional[str] = None
    old_value: Any = None
    new_value: Any = None
    motif: Optional[str] = None
    metadata: Optional[dict] = None


@dataclass
class AuditEntryDTO:
    """
    DTO pour la représentation d'une entrée d'audit.

    Utilisé pour les réponses API et l'affichage côté client.
    """

    id: str  # UUID as string
    entity_type: str
    entity_id: str
    action: str
    field_name: Optional[str]
    old_value: Optional[str]
    new_value: Optional[str]
    author_id: int
    author_name: str
    timestamp: datetime
    motif: Optional[str]
    metadata: Optional[dict]

    @staticmethod
    def from_entity(entry: AuditEntry) -> "AuditEntryDTO":
        """
        Convertit une entité AuditEntry en DTO.

        Args:
            entry: L'entité AuditEntry source.

        Returns:
            AuditEntryDTO correspondant.
        """
        return AuditEntryDTO(
            id=str(entry.id),
            entity_type=entry.entity_type,
            entity_id=entry.entity_id,
            action=entry.action,
            field_name=entry.field_name,
            old_value=entry.old_value,
            new_value=entry.new_value,
            author_id=entry.author_id,
            author_name=entry.author_name,
            timestamp=entry.timestamp,
            motif=entry.motif,
            metadata=entry.metadata,
        )


@dataclass
class GetHistoryDTO:
    """DTO pour récupérer l'historique d'une entité."""

    entity_type: str
    entity_id: str
    limit: int = 50
    offset: int = 0


@dataclass
class GetUserActionsDTO:
    """DTO pour récupérer les actions d'un utilisateur."""

    author_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    entity_type: Optional[str] = None
    limit: int = 100
    offset: int = 0


@dataclass
class GetRecentEntriesDTO:
    """DTO pour récupérer les entrées récentes."""

    entity_type: Optional[str] = None
    action: Optional[str] = None
    limit: int = 50


@dataclass
class SearchAuditDTO:
    """DTO pour la recherche avancée d'entrées d'audit."""

    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    action: Optional[str] = None
    author_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 100
    offset: int = 0


@dataclass
class AuditHistoryResponseDTO:
    """DTO pour la réponse contenant l'historique d'audit."""

    entries: List[AuditEntryDTO]
    total: int
    limit: int
    offset: int

    @property
    def has_more(self) -> bool:
        """Indique s'il y a plus d'entrées disponibles."""
        return (self.offset + self.limit) < self.total
