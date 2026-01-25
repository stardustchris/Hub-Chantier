"""Entite Notification."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

from ..value_objects import NotificationType


@dataclass
class Notification:
    """
    Entite representant une notification utilisateur.

    Une notification informe un utilisateur d'un evenement
    qui le concerne (mention, commentaire, document, etc.).

    Attributes:
        id: Identifiant unique.
        user_id: ID de l'utilisateur destinataire.
        type: Type de notification.
        title: Titre court de la notification.
        message: Message detaille.
        is_read: Statut de lecture.
        related_post_id: ID du post concerne (optionnel).
        related_comment_id: ID du commentaire concerne (optionnel).
        related_chantier_id: ID du chantier concerne (optionnel).
        related_document_id: ID du document concerne (optionnel).
        triggered_by_user_id: ID de l'utilisateur ayant declenche la notification.
        metadata: Donnees supplementaires (JSON).
        created_at: Date de creation.
        read_at: Date de lecture.
    """

    user_id: int
    type: NotificationType
    title: str
    message: str
    id: Optional[int] = None
    is_read: bool = False
    related_post_id: Optional[int] = None
    related_comment_id: Optional[int] = None
    related_chantier_id: Optional[int] = None
    related_document_id: Optional[int] = None
    triggered_by_user_id: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    read_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validation a la creation."""
        if not self.title or not self.title.strip():
            raise ValueError("Le titre ne peut pas etre vide")
        if not self.message or not self.message.strip():
            raise ValueError("Le message ne peut pas etre vide")
        self.title = self.title.strip()
        self.message = self.message.strip()

    def mark_as_read(self) -> None:
        """Marque la notification comme lue."""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.now()

    def mark_as_unread(self) -> None:
        """Marque la notification comme non lue."""
        self.is_read = False
        self.read_at = None

    @property
    def is_unread(self) -> bool:
        """Retourne True si la notification n'a pas ete lue."""
        return not self.is_read

    def __eq__(self, other: object) -> bool:
        """Egalite basee sur l'ID."""
        if not isinstance(other, Notification):
            return False
        if self.id is None or other.id is None:
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash base sur l'ID."""
        return hash(self.id) if self.id else hash(id(self))
