"""Add audit_log table

Revision ID: audit_log_001
Revises: 20260201_1600_add_devis_support_to_lot_budgetaire
Create Date: 2026-02-01 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "audit_log_001"
down_revision = "20260201_1600_add_devis_support_to_lot_budgetaire"
branch_labels = None
depends_on = None


def upgrade():
    """
    Crée la table audit_log pour le système d'audit trail générique.

    Cette table permet de tracer toutes les modifications effectuées sur les entités
    métier de tous les modules (devis, lots budgétaires, achats, etc.).

    Caractéristiques :
    - Table append-only (pas de mise à jour, pas de suppression)
    - UUID comme clé primaire pour compatibilité cross-module
    - JSONB pour métadonnées (support JSON natif PostgreSQL)
    - Index optimisés pour requêtes fréquentes
    """
    # Création de la table audit_log
    op.create_table(
        "audit_log",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
            comment="Identifiant unique UUID",
        ),
        sa.Column(
            "entity_type",
            sa.String(length=100),
            nullable=False,
            comment="Type de l'entité (devis, lot_budgetaire, achat, etc.)",
        ),
        sa.Column(
            "entity_id",
            sa.String(length=100),
            nullable=False,
            comment="ID de l'entité (string pour support UUID et int)",
        ),
        sa.Column(
            "action",
            sa.String(length=50),
            nullable=False,
            comment="Action (created, updated, deleted, status_changed, validated, etc.)",
        ),
        sa.Column(
            "field_name",
            sa.String(length=100),
            nullable=True,
            comment="Nom du champ modifié (NULL pour création/suppression globale)",
        ),
        sa.Column(
            "old_value",
            sa.Text(),
            nullable=True,
            comment="Valeur avant modification (JSON serialized)",
        ),
        sa.Column(
            "new_value",
            sa.Text(),
            nullable=True,
            comment="Valeur après modification (JSON serialized)",
        ),
        sa.Column(
            "author_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
            comment="ID de l'utilisateur auteur de l'action",
        ),
        sa.Column(
            "author_name",
            sa.String(length=200),
            nullable=False,
            comment="Nom complet de l'utilisateur (dénormalisé pour performance)",
        ),
        sa.Column(
            "timestamp",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("timezone('utc', now())"),
            comment="Date et heure de l'action (UTC)",
        ),
        sa.Column(
            "motif",
            sa.Text(),
            nullable=True,
            comment="Raison de la modification (optionnel)",
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Métadonnées additionnelles au format JSON",
        ),
        sa.PrimaryKeyConstraint("id"),
        comment="Table d'audit trail générique pour tous les modules (append-only)",
    )

    # Index pour optimisation des requêtes fréquentes
    op.create_index(
        "ix_audit_log_entity_type",
        "audit_log",
        ["entity_type"],
    )

    op.create_index(
        "ix_audit_log_action",
        "audit_log",
        ["action"],
    )

    op.create_index(
        "ix_audit_log_author_id",
        "audit_log",
        ["author_id"],
    )

    op.create_index(
        "ix_audit_log_timestamp",
        "audit_log",
        ["timestamp"],
    )

    # Index composite pour récupération historique entité
    op.create_index(
        "ix_audit_log_entity_type_entity_id",
        "audit_log",
        ["entity_type", "entity_id"],
    )

    # Index composite pour feed d'activité par type
    op.create_index(
        "ix_audit_log_entity_type_timestamp",
        "audit_log",
        ["entity_type", "timestamp"],
    )

    # Index composite pour actions utilisateur triées
    op.create_index(
        "ix_audit_log_author_id_timestamp",
        "audit_log",
        ["author_id", "timestamp"],
    )

    # Index composite pour recherche par type d'action
    op.create_index(
        "ix_audit_log_action_timestamp",
        "audit_log",
        ["action", "timestamp"],
    )


def downgrade():
    """Supprime la table audit_log et ses index."""
    op.drop_index("ix_audit_log_action_timestamp", table_name="audit_log")
    op.drop_index("ix_audit_log_author_id_timestamp", table_name="audit_log")
    op.drop_index("ix_audit_log_entity_type_timestamp", table_name="audit_log")
    op.drop_index("ix_audit_log_entity_type_entity_id", table_name="audit_log")
    op.drop_index("ix_audit_log_timestamp", table_name="audit_log")
    op.drop_index("ix_audit_log_author_id", table_name="audit_log")
    op.drop_index("ix_audit_log_action", table_name="audit_log")
    op.drop_index("ix_audit_log_entity_type", table_name="audit_log")
    op.drop_table("audit_log")
