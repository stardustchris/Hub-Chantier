"""Initial chantiers schema with soft delete and audit trail.

Revision ID: 0001
Revises:
Create Date: 2026-01-24 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create chantiers tables with soft delete support."""

    # Create chantiers table (if not exists, with soft delete)
    op.execute("""
        ALTER TABLE chantiers
        ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP NULL;
    """)

    # Create audit_logs table for tracking changes
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('entity_type', sa.String(100), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('old_values', sa.JSON(), nullable=True),
        sa.Column('new_values', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes for audit_logs
    op.create_index('ix_audit_logs_entity', 'audit_logs', ['entity_type', 'entity_id'])
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])


def downgrade() -> None:
    """Remove soft delete and audit trail."""

    # Drop audit_logs table
    op.drop_index('ix_audit_logs_action')
    op.drop_index('ix_audit_logs_created_at')
    op.drop_index('ix_audit_logs_user_id')
    op.drop_index('ix_audit_logs_entity')
    op.drop_table('audit_logs')

    # Remove deleted_at column
    op.execute("""
        ALTER TABLE chantiers
        DROP COLUMN IF EXISTS deleted_at;
    """)
