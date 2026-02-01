"""Add devis support to lot_budgetaire

Revision ID: add_devis_support
Revises: 20260131_0001
Create Date: 2026-02-01 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20260201_1600_add_devis_support_to_lot_budgetaire'
down_revision: Union[str, None] = '20260131_0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add devis support columns to lots_budgetaires table.

    This migration adds support for the "Devis" (quote) phase by:
    1. Making budget_id nullable (lots can now belong to either a budget or a devis)
    2. Adding devis_id column (UUID as string)
    3. Adding detailed cost breakdown columns (debourse_*)
    4. Adding margin columns (marge_pct, prix_vente_ht)
    5. Adding XOR constraint (devis_id XOR budget_id)
    """

    # 1. Make budget_id nullable
    op.alter_column(
        'lots_budgetaires',
        'budget_id',
        existing_type=sa.Integer(),
        nullable=True
    )

    # 2. Add devis_id column
    op.add_column(
        'lots_budgetaires',
        sa.Column('devis_id', sa.String(36), nullable=True)
    )

    # 3. Add detailed cost breakdown columns (debourse_*)
    op.add_column(
        'lots_budgetaires',
        sa.Column('debourse_main_oeuvre', sa.Numeric(12, 2), nullable=True)
    )
    op.add_column(
        'lots_budgetaires',
        sa.Column('debourse_materiaux', sa.Numeric(12, 2), nullable=True)
    )
    op.add_column(
        'lots_budgetaires',
        sa.Column('debourse_sous_traitance', sa.Numeric(12, 2), nullable=True)
    )
    op.add_column(
        'lots_budgetaires',
        sa.Column('debourse_materiel', sa.Numeric(12, 2), nullable=True)
    )
    op.add_column(
        'lots_budgetaires',
        sa.Column('debourse_divers', sa.Numeric(12, 2), nullable=True)
    )

    # 4. Add margin columns
    op.add_column(
        'lots_budgetaires',
        sa.Column('marge_pct', sa.Numeric(5, 2), nullable=True)
    )
    op.add_column(
        'lots_budgetaires',
        sa.Column('prix_vente_ht', sa.Numeric(12, 2), nullable=True)
    )

    # 5. Create indexes for devis_id
    op.create_index(
        'ix_lots_budgetaires_devis_id',
        'lots_budgetaires',
        ['devis_id']
    )
    op.create_index(
        'ix_lots_budgetaires_devis_ordre',
        'lots_budgetaires',
        ['devis_id', 'ordre']
    )

    # 6. Drop the old unique constraint on (budget_id, code_lot)
    # because it doesn't handle NULL budget_id correctly
    op.drop_constraint(
        'uq_lots_budgetaires_budget_code',
        'lots_budgetaires',
        type_='unique'
    )

    # 7. Add CHECK constraints

    # XOR constraint: either devis_id or budget_id must be set, but not both
    op.create_check_constraint(
        'check_lots_budgetaires_devis_xor_budget',
        'lots_budgetaires',
        '(devis_id IS NULL AND budget_id IS NOT NULL) OR (devis_id IS NOT NULL AND budget_id IS NULL)'
    )

    # Debourse constraints (all must be >= 0 if set)
    op.create_check_constraint(
        'check_lots_budgetaires_debourse_mo_positive',
        'lots_budgetaires',
        'debourse_main_oeuvre IS NULL OR debourse_main_oeuvre >= 0'
    )
    op.create_check_constraint(
        'check_lots_budgetaires_debourse_mat_positive',
        'lots_budgetaires',
        'debourse_materiaux IS NULL OR debourse_materiaux >= 0'
    )
    op.create_check_constraint(
        'check_lots_budgetaires_debourse_st_positive',
        'lots_budgetaires',
        'debourse_sous_traitance IS NULL OR debourse_sous_traitance >= 0'
    )
    op.create_check_constraint(
        'check_lots_budgetaires_debourse_materiel_positive',
        'lots_budgetaires',
        'debourse_materiel IS NULL OR debourse_materiel >= 0'
    )
    op.create_check_constraint(
        'check_lots_budgetaires_debourse_divers_positive',
        'lots_budgetaires',
        'debourse_divers IS NULL OR debourse_divers >= 0'
    )

    # Marge constraints
    op.create_check_constraint(
        'check_lots_budgetaires_marge_positive',
        'lots_budgetaires',
        'marge_pct IS NULL OR marge_pct >= 0'
    )
    op.create_check_constraint(
        'check_lots_budgetaires_prix_vente_positive',
        'lots_budgetaires',
        'prix_vente_ht IS NULL OR prix_vente_ht >= 0'
    )


def downgrade() -> None:
    """Revert devis support changes."""

    # Drop CHECK constraints
    op.drop_constraint('check_lots_budgetaires_prix_vente_positive', 'lots_budgetaires', type_='check')
    op.drop_constraint('check_lots_budgetaires_marge_positive', 'lots_budgetaires', type_='check')
    op.drop_constraint('check_lots_budgetaires_debourse_divers_positive', 'lots_budgetaires', type_='check')
    op.drop_constraint('check_lots_budgetaires_debourse_materiel_positive', 'lots_budgetaires', type_='check')
    op.drop_constraint('check_lots_budgetaires_debourse_st_positive', 'lots_budgetaires', type_='check')
    op.drop_constraint('check_lots_budgetaires_debourse_mat_positive', 'lots_budgetaires', type_='check')
    op.drop_constraint('check_lots_budgetaires_debourse_mo_positive', 'lots_budgetaires', type_='check')
    op.drop_constraint('check_lots_budgetaires_devis_xor_budget', 'lots_budgetaires', type_='check')

    # Recreate the unique constraint on (budget_id, code_lot)
    op.create_unique_constraint(
        'uq_lots_budgetaires_budget_code',
        'lots_budgetaires',
        ['budget_id', 'code_lot']
    )

    # Drop indexes
    op.drop_index('ix_lots_budgetaires_devis_ordre', table_name='lots_budgetaires')
    op.drop_index('ix_lots_budgetaires_devis_id', table_name='lots_budgetaires')

    # Drop new columns
    op.drop_column('lots_budgetaires', 'prix_vente_ht')
    op.drop_column('lots_budgetaires', 'marge_pct')
    op.drop_column('lots_budgetaires', 'debourse_divers')
    op.drop_column('lots_budgetaires', 'debourse_materiel')
    op.drop_column('lots_budgetaires', 'debourse_sous_traitance')
    op.drop_column('lots_budgetaires', 'debourse_materiaux')
    op.drop_column('lots_budgetaires', 'debourse_main_oeuvre')
    op.drop_column('lots_budgetaires', 'devis_id')

    # Make budget_id NOT NULL again
    op.alter_column(
        'lots_budgetaires',
        'budget_id',
        existing_type=sa.Integer(),
        nullable=False
    )
