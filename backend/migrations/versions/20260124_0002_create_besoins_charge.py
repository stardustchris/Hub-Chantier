"""Create besoins_charge table for planning de charge module.

Revision ID: 20260124_0002
Revises: 20260124_0001
Create Date: 2026-01-24

Implements CDC Section 6 - Planning de Charge (PDC-01 to PDC-17)
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260124_0002"
down_revision = "20260124_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create besoins_charge table with indexes and foreign keys."""
    op.create_table(
        "besoins_charge",
        # Primary key
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        # Foreign keys
        sa.Column("chantier_id", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        # Semaine
        sa.Column("semaine_annee", sa.Integer(), nullable=False),
        sa.Column("semaine_numero", sa.Integer(), nullable=False),
        # Besoin
        sa.Column("type_metier", sa.String(50), nullable=False),
        sa.Column("besoin_heures", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("note", sa.Text(), nullable=True),
        # Soft delete
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("deleted_by", sa.Integer(), nullable=True),
        # Timestamps
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        # Constraints
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["chantier_id"],
            ["chantiers.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["created_by"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["deleted_by"],
            ["users.id"],
            ondelete="SET NULL",
        ),
    )

    # Indexes
    op.create_index(
        "ix_besoins_charge_chantier_id",
        "besoins_charge",
        ["chantier_id"],
    )
    op.create_index(
        "ix_besoins_charge_chantier_semaine",
        "besoins_charge",
        ["chantier_id", "semaine_annee", "semaine_numero"],
    )
    op.create_index(
        "ix_besoins_charge_semaine",
        "besoins_charge",
        ["semaine_annee", "semaine_numero"],
    )
    op.create_index(
        "ix_besoins_charge_unique",
        "besoins_charge",
        ["chantier_id", "semaine_annee", "semaine_numero", "type_metier"],
        unique=True,
    )
    op.create_index(
        "ix_besoins_charge_not_deleted",
        "besoins_charge",
        ["is_deleted"],
    )


def downgrade() -> None:
    """Drop besoins_charge table and indexes."""
    op.drop_index("ix_besoins_charge_not_deleted", table_name="besoins_charge")
    op.drop_index("ix_besoins_charge_unique", table_name="besoins_charge")
    op.drop_index("ix_besoins_charge_semaine", table_name="besoins_charge")
    op.drop_index("ix_besoins_charge_chantier_semaine", table_name="besoins_charge")
    op.drop_index("ix_besoins_charge_chantier_id", table_name="besoins_charge")
    op.drop_table("besoins_charge")
