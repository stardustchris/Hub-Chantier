"""SQLAlchemy Model APIKeyModel - Persistence clés API."""

import json
from typing import List
from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    func,
    event,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property

from shared.infrastructure.database_base import Base


class APIKeyModel(Base):
    """
    Modèle SQLAlchemy pour la table api_keys.

    Stocke les clés API pour l'authentification de l'API publique v1.
    Le secret n'est JAMAIS stocké en clair, uniquement son hash SHA256.

    Table: api_keys

    Compatibilité SQLite/PostgreSQL:
    - id: UUID (PostgreSQL) ou String(36) (SQLite)
    - scopes: ARRAY (PostgreSQL) ou Text JSON (SQLite)
    """

    __tablename__ = "api_keys"
    __table_args__ = {"extend_existing": True}

    # Colonnes
    id = Column(String(36), primary_key=True, nullable=False)  # Compatible SQLite et PostgreSQL
    key_hash = Column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        comment="SHA256 hash du secret (jamais stocké en clair)",
    )
    key_prefix = Column(
        String(8), nullable=False, comment="Préfixe pour affichage (hbc_xxxx...)"
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Utilisateur propriétaire de la clé",
    )
    nom = Column(String(255), nullable=False, comment="Nom descriptif de la clé")
    description = Column(Text, nullable=True, comment="Description détaillée")
    _scopes = Column(
        "scopes",
        Text,
        nullable=False,
        server_default='["read"]',
        comment="Permissions accordées (read, write, admin) - JSON pour compatibilité SQLite",
    )
    rate_limit_per_hour = Column(
        Integer,
        nullable=False,
        server_default="1000",
        comment="Limite de requêtes par heure",
    )
    is_active = Column(
        Boolean,
        nullable=False,
        server_default="true",
        index=True,
        comment="Clé active ou révoquée",
    )
    last_used_at = Column(
        DateTime, nullable=True, comment="Dernière utilisation (audit)"
    )
    expires_at = Column(
        DateTime, nullable=True, index=True, comment="Date d'expiration (NULL = jamais)"
    )
    created_at = Column(
        DateTime, nullable=False, server_default=func.now(), comment="Date de création"
    )

    @hybrid_property
    def scopes(self) -> List[str]:
        """Récupère les scopes en tant que liste Python."""
        if self._scopes:
            try:
                return json.loads(self._scopes) if isinstance(self._scopes, str) else self._scopes
            except (json.JSONDecodeError, TypeError):
                return ["read"]
        return ["read"]

    @scopes.setter
    def scopes(self, value: List[str]) -> None:
        """Stocke les scopes en JSON string pour compatibilité SQLite."""
        if isinstance(value, list):
            self._scopes = json.dumps(value)
        elif isinstance(value, str):
            self._scopes = value
        else:
            self._scopes = '["read"]'

    # Relations
    user = relationship("UserModel", back_populates="api_keys")

    def __repr__(self) -> str:
        """Représentation string du modèle."""
        return (
            f"<APIKeyModel(id={self.id}, "
            f"prefix={self.key_prefix}, "
            f"user_id={self.user_id}, "
            f"active={self.is_active})>"
        )
