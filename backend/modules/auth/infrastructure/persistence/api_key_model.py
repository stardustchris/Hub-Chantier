"""SQLAlchemy Model APIKeyModel - Persistence clés API."""

from sqlalchemy import (
    Column,
    String,
    Integer,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship

from shared.infrastructure.database_base import Base


class APIKeyModel(Base):
    """
    Modèle SQLAlchemy pour la table api_keys.

    Stocke les clés API pour l'authentification de l'API publique v1.
    Le secret n'est JAMAIS stocké en clair, uniquement son hash SHA256.

    Table: api_keys
    """

    __tablename__ = "api_keys"
    __table_args__ = {"extend_existing": True}

    # Colonnes
    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
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
    scopes = Column(
        ARRAY(String),
        nullable=False,
        server_default="ARRAY['read']::text[]",
        comment="Permissions accordées (read, write, admin)",
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
