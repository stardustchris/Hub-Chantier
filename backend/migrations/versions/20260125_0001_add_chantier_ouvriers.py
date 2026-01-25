"""Add chantier_ouvriers table for managing ouvriers/interimaires/sous-traitants.

Revision ID: 20260125_0001
Revises: 20260124_0003_logistique_schema
Create Date: 2026-01-25

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260125_0001'
down_revision = '20260124_0003_logistique_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create chantier_ouvriers table."""
    op.create_table(
        'chantier_ouvriers',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('chantier_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['chantier_id'], ['chantiers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('chantier_id', 'user_id', name='uq_chantier_ouvrier')
    )
    op.create_index('ix_chantier_ouvriers_user_id', 'chantier_ouvriers', ['user_id'])
    op.create_index('ix_chantier_ouvriers_chantier_id', 'chantier_ouvriers', ['chantier_id'])


def downgrade() -> None:
    """Drop chantier_ouvriers table."""
    op.drop_index('ix_chantier_ouvriers_chantier_id', table_name='chantier_ouvriers')
    op.drop_index('ix_chantier_ouvriers_user_id', table_name='chantier_ouvriers')
    op.drop_table('chantier_ouvriers')
