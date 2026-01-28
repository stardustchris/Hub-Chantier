"""SQLAlchemy Models pour les Webhooks."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ARRAY, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from shared.infrastructure.database_base import Base


class WebhookModel(Base):
    """
    Modèle SQLAlchemy pour les webhooks.

    Stocke la configuration des webhooks utilisateurs:
    - URL destination
    - Événements à écouter (avec pattern matching)
    - Secret HMAC pour les signatures
    - Statut et historique de retry
    """

    __tablename__ = "webhooks"
    __table_args__ = {"extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Configuration
    url = Column(String(500), nullable=False, comment="URL destination du webhook")
    events = Column(ARRAY(String), nullable=False, comment="Patterns d'événements (ex: chantier.*, heures.*)")
    secret = Column(String(64), nullable=False, comment="Secret pour signatures HMAC-SHA256")
    description = Column(Text, nullable=True, comment="Description du webhook")

    # État
    is_active = Column(Boolean, server_default="true", nullable=False, comment="Webhook actif ou désactivé")
    last_triggered_at = Column(DateTime, nullable=True, comment="Dernière exécution réussie")
    consecutive_failures = Column(Integer, server_default="0", nullable=False, comment="Nombre d'échecs consécutifs")

    # Retry configuration
    retry_enabled = Column(Boolean, server_default="true", nullable=False, comment="Retry automatique activé")
    max_retries = Column(Integer, server_default="3", nullable=False, comment="Nombre max de tentatives")

    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relations
    user = relationship("UserModel", back_populates="webhooks")
    deliveries = relationship(
        "WebhookDeliveryModel",
        back_populates="webhook",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<WebhookModel(id={self.id}, user_id={self.user_id}, url={self.url}, is_active={self.is_active})>"


class WebhookDeliveryModel(Base):
    """
    Modèle SQLAlchemy pour l'historique des tentatives de livraison.

    Trace chaque tentative de livraison d'un webhook:
    - Événement livré
    - Code HTTP et réponse
    - Timing et numéro de tentative
    """

    __tablename__ = "webhook_deliveries"
    __table_args__ = {"extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    webhook_id = Column(UUID(as_uuid=True), ForeignKey("webhooks.id", ondelete="CASCADE"), nullable=False)

    # Événement
    event_type = Column(String(100), nullable=False, comment="Type d'événement (ex: chantier.created)")
    payload = Column(JSONB, nullable=False, comment="Payload JSON de l'événement")

    # Résultat de la livraison
    status_code = Column(Integer, nullable=True, comment="Code HTTP de la réponse")
    response_body = Column(Text, nullable=True, comment="Corps de la réponse (limité 1000 chars)")
    success = Column(Boolean, nullable=True, comment="Livraison réussie (HTTP 2xx)")
    error_message = Column(Text, nullable=True, comment="Message d'erreur si échec")

    # Timing
    delivered_at = Column(DateTime, server_default=func.now(), nullable=False, comment="Timestamp de la tentative")
    response_time_ms = Column(Integer, nullable=True, comment="Temps de réponse en ms")

    # Retry
    attempt_number = Column(Integer, server_default="1", nullable=False, comment="Numéro de tentative")

    # Relations
    webhook = relationship("WebhookModel", back_populates="deliveries")

    def __repr__(self) -> str:
        return f"<WebhookDeliveryModel(id={self.id}, webhook_id={self.webhook_id}, event={self.event_type}, attempt={self.attempt_number})>"
