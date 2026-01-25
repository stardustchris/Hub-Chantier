"""DTOs pour le module notifications."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class NotificationDTO(BaseModel):
    """DTO de sortie pour une notification."""

    id: int
    user_id: int
    type: str
    title: str
    message: str
    is_read: bool
    read_at: Optional[datetime] = None
    related_post_id: Optional[int] = None
    related_comment_id: Optional[int] = None
    related_chantier_id: Optional[int] = None
    related_document_id: Optional[int] = None
    triggered_by_user_id: Optional[int] = None
    triggered_by_user_name: Optional[str] = None  # Enrichi par le service
    chantier_name: Optional[str] = None  # Enrichi par le service
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListDTO(BaseModel):
    """DTO de sortie pour une liste de notifications."""

    notifications: list[NotificationDTO]
    unread_count: int
    total: int


class MarkAsReadDTO(BaseModel):
    """DTO d'entree pour marquer comme lu."""

    notification_ids: Optional[list[int]] = None  # Si None, marque toutes comme lues


class CreateNotificationDTO(BaseModel):
    """DTO d'entree pour creer une notification."""

    user_id: int
    type: str
    title: str
    message: str
    related_post_id: Optional[int] = None
    related_comment_id: Optional[int] = None
    related_chantier_id: Optional[int] = None
    related_document_id: Optional[int] = None
    triggered_by_user_id: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
