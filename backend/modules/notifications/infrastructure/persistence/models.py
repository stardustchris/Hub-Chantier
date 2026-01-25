"""Modeles SQLAlchemy pour le module notifications."""

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    Index,
    JSON,
)

from shared.infrastructure.database_base import Base


class NotificationModel(Base):
    """
    Modele SQLAlchemy pour les notifications.

    Stocke les notifications envoyees aux utilisateurs.
    """

    __tablename__ = "notifications"

    # Identifiant
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Destinataire
    user_id = Column(Integer, nullable=False, index=True)

    # Type de notification
    type = Column(String(50), nullable=False, index=True)

    # Contenu
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # Statut de lecture
    is_read = Column(Boolean, nullable=False, default=False, index=True)
    read_at = Column(DateTime, nullable=True)

    # Relations vers d'autres entites (optionnelles)
    related_post_id = Column(Integer, nullable=True, index=True)
    related_comment_id = Column(Integer, nullable=True)
    related_chantier_id = Column(Integer, nullable=True, index=True)
    related_document_id = Column(Integer, nullable=True)

    # Utilisateur ayant declenche la notification
    triggered_by_user_id = Column(Integer, nullable=True, index=True)

    # Metadata supplementaires (JSON)
    metadata = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.now, index=True)

    # Index compose pour les requetes frequentes
    __table_args__ = (
        Index("ix_notifications_user_unread", "user_id", "is_read", "created_at"),
        Index("ix_notifications_user_created", "user_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<NotificationModel(id={self.id}, user_id={self.user_id}, type={self.type})>"
