"""Modèle SQLAlchemy pour l'audit trail."""


from sqlalchemy import Column, Integer, String, DateTime, JSON, Index
from sqlalchemy.sql import func

from shared.infrastructure.database_base import Base


class AuditLog(Base):
    """
    Modèle SQLAlchemy pour tracer les actions sur les entités.

    Permet de garder un historique des modifications pour :
    - Conformité RGPD (traçabilité des accès aux données)
    - Audit de sécurité
    - Debug et support

    Attributes:
        id: Identifiant unique de l'entrée d'audit.
        entity_type: Type d'entité (ex: "chantier", "user").
        entity_id: ID de l'entité concernée.
        action: Action effectuée (created, updated, deleted, status_changed, etc.).
        user_id: ID de l'utilisateur ayant effectué l'action.
        old_values: Valeurs avant modification (JSON).
        new_values: Valeurs après modification (JSON).
        ip_address: Adresse IP de l'utilisateur.
        user_agent: User-Agent du navigateur/client.
        created_at: Date et heure de l'action.
    """

    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_entity", "entity_type", "entity_id"),
        Index("ix_audit_logs_user_id", "user_id"),
        Index("ix_audit_logs_created_at", "created_at"),
        Index("ix_audit_logs_action", "action"),
        {"extend_existing": True},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)
    user_id = Column(Integer, nullable=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action}, entity={self.entity_type}:{self.entity_id})>"
