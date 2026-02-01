"""Modèles SQLAlchemy pour le module Audit."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Text,
    Index,
    ForeignKey,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PostgreSQL_UUID, JSONB

from shared.infrastructure.database_base import Base


class AuditLogModel(Base):
    """
    Modèle SQLAlchemy pour les entrées d'audit.

    Table append-only (pas de mise à jour, pas de suppression) pour garantir
    l'intégrité de l'audit trail.

    Optimisations :
    - Index sur entity_type + entity_id (requêtes d'historique fréquentes)
    - Index sur author_id (requêtes par utilisateur)
    - Index sur timestamp (tri chronologique)
    - Index composite entity_type + timestamp (feed d'activité par type)
    - JSONB pour metadata (support JSON natif PostgreSQL)
    """

    __tablename__ = "audit_log"

    # Clé primaire UUID
    id = Column(
        PostgreSQL_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        comment="Identifiant unique UUID",
    )

    # Entité auditée
    entity_type = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Type de l'entité (devis, lot_budgetaire, achat, etc.)",
    )

    entity_id = Column(
        String(100),
        nullable=False,
        comment="ID de l'entité (string pour support UUID et int)",
    )

    # Action effectuée
    action = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Action (created, updated, deleted, status_changed, validated, etc.)",
    )

    # Détails de la modification
    field_name = Column(
        String(100),
        nullable=True,
        comment="Nom du champ modifié (NULL pour création/suppression globale)",
    )

    old_value = Column(
        Text,
        nullable=True,
        comment="Valeur avant modification (JSON serialized)",
    )

    new_value = Column(
        Text,
        nullable=True,
        comment="Valeur après modification (JSON serialized)",
    )

    # Auteur
    author_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="ID de l'utilisateur auteur de l'action",
    )

    author_name = Column(
        String(200),
        nullable=False,
        comment="Nom complet de l'utilisateur (dénormalisé pour performance)",
    )

    # Timestamp
    timestamp = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="Date et heure de l'action (UTC)",
    )

    # Contexte
    motif = Column(
        Text,
        nullable=True,
        comment="Raison de la modification (optionnel)",
    )

    metadata = Column(
        JSONB,
        nullable=True,
        comment="Métadonnées additionnelles au format JSON",
    )

    __table_args__ = (
        # Index composite pour optimisation des requêtes fréquentes
        Index(
            "ix_audit_log_entity_type_entity_id",
            "entity_type",
            "entity_id",
            comment="Index pour récupération historique entité",
        ),
        Index(
            "ix_audit_log_entity_type_timestamp",
            "entity_type",
            "timestamp",
            comment="Index pour feed d'activité par type",
        ),
        Index(
            "ix_audit_log_author_id_timestamp",
            "author_id",
            "timestamp",
            comment="Index pour actions utilisateur triées",
        ),
        Index(
            "ix_audit_log_action_timestamp",
            "action",
            "timestamp",
            comment="Index pour recherche par type d'action",
        ),
        {
            "comment": "Table d'audit trail générique pour tous les modules (append-only)",
        },
    )

    def __repr__(self) -> str:
        """Représentation string pour debug."""
        return (
            f"<AuditLogModel(id={self.id}, entity_type='{self.entity_type}', "
            f"entity_id='{self.entity_id}', action='{self.action}', "
            f"timestamp={self.timestamp})>"
        )
