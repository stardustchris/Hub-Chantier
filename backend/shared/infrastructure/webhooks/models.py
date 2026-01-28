"""SQLAlchemy Models pour les Webhooks."""

import json
from datetime import datetime
from typing import List, Dict, Any
from uuid import uuid4

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.ext.hybrid import hybrid_property
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

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Configuration
    url = Column(String(500), nullable=False, comment="URL destination du webhook")
    _events = Column("events", Text, nullable=False, comment="Patterns d'événements - JSON pour compatibilité SQLite")
    secret = Column(String(64), nullable=False, comment="Secret pour signatures HMAC-SHA256")
    description = Column(Text, nullable=True, comment="Description du webhook")

    @hybrid_property
    def events(self) -> List[str]:
        """Récupère les événements en tant que liste Python."""
        if self._events:
            try:
                return json.loads(self._events) if isinstance(self._events, str) else self._events
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    @events.setter
    def events(self, value: List[str]) -> None:
        """Stocke les événements en JSON string pour compatibilité SQLite."""
        if isinstance(value, list):
            self._events = json.dumps(value)
        elif isinstance(value, str):
            self._events = value
        else:
            self._events = '[]'

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

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    webhook_id = Column(String(36), ForeignKey("webhooks.id", ondelete="CASCADE"), nullable=False)

    # Événement
    event_type = Column(String(100), nullable=False, comment="Type d'événement (ex: chantier.created)")
    _payload = Column("payload", Text, nullable=False, comment="Payload JSON de l'événement - Text pour compatibilité SQLite")

    @hybrid_property
    def payload(self) -> Dict[str, Any]:
        """Récupère le payload en tant que dict Python."""
        if self._payload:
            try:
                return json.loads(self._payload) if isinstance(self._payload, str) else self._payload
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}

    @payload.setter
    def payload(self, value: Dict[str, Any]) -> None:
        """Stocke le payload en JSON string pour compatibilité SQLite."""
        if isinstance(value, dict):
            self._payload = json.dumps(value)
        elif isinstance(value, str):
            self._payload = value
        else:
            self._payload = '{}'

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
