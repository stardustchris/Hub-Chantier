"""GAP #6: Add devis_id to budgets table for quote-to-budget traceability.

Allows tracking which quote (devis) originated each budget.
No foreign key to avoid cross-module coupling in the database.

Revision ID: add_devis_id_budget_001
Revises: signatures_devis_001
Create Date: 2026-02-02 20:00:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_devis_id_budget_001'
down_revision: Union[str, None] = 'signatures_devis_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'budgets',
        sa.Column('devis_id', sa.Integer(), nullable=True),
    )
    op.create_index(
        'ix_budgets_devis_id',
        'budgets',
        ['devis_id'],
    )


def downgrade() -> None:
    op.drop_index('ix_budgets_devis_id', table_name='budgets')
    op.drop_column('budgets', 'devis_id')
