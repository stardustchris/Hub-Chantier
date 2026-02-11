"""Retirer TVA 2.1% des CHECK constraints achats et situations.

Le taux 2.1% (presse/medicaments) ne s'applique pas au BTP.
Les taux legaux BTP sont: 0% (exonere/autoliquidation), 5.5% (renovation
energetique), 10% (travaux amelioration logement >2 ans), 20% (taux normal).
Aligne les CHECK SQL avec Python TAUX_VALIDES = [0, 5.5, 10, 20].

Revision ID: remove_tva_21
Revises: audit_financial_constraints
Create Date: 2026-02-11
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "remove_tva_21"
down_revision = "audit_financial_constraints"
branch_labels = None
depends_on = None


def upgrade():
    # ── Achats: retirer 2.1% du CHECK TVA ──────────────────────────────
    op.execute(
        "ALTER TABLE achats DROP CONSTRAINT "
        "IF EXISTS check_achats_tva_range"
    )
    op.execute(
        "ALTER TABLE achats ADD CONSTRAINT check_achats_tva_range "
        "CHECK (taux_tva IN (0, 5.5, 10, 20))"
    )

    # ── Situations: retirer 2.1% du CHECK TVA ──────────────────────────
    op.execute(
        "ALTER TABLE situations_travaux DROP CONSTRAINT "
        "IF EXISTS check_situations_travaux_tva_range"
    )
    op.execute(
        "ALTER TABLE situations_travaux ADD CONSTRAINT check_situations_travaux_tva_range "
        "CHECK (taux_tva IN (0, 5.5, 10, 20))"
    )


def downgrade():
    # ── Restaurer avec 2.1% ────────────────────────────────────────────
    op.execute(
        "ALTER TABLE situations_travaux DROP CONSTRAINT "
        "IF EXISTS check_situations_travaux_tva_range"
    )
    op.execute(
        "ALTER TABLE situations_travaux ADD CONSTRAINT check_situations_travaux_tva_range "
        "CHECK (taux_tva IN (0, 2.1, 5.5, 10, 20))"
    )

    op.execute(
        "ALTER TABLE achats DROP CONSTRAINT "
        "IF EXISTS check_achats_tva_range"
    )
    op.execute(
        "ALTER TABLE achats ADD CONSTRAINT check_achats_tva_range "
        "CHECK (taux_tva IN (0, 2.1, 5.5, 10, 20))"
    )
