"""Fix coeff_frais_generaux: ratio (0.12) -> pourcentage (12.00).

Bug critique: la colonne Numeric(5,4) stockait un ratio (0.12) alors que
le domaine et le calcul attendent un pourcentage (12 = 12%).
- Change le type de Numeric(5,4) vers Numeric(5,2)
- Convertit les donnees existantes: valeurs < 1 sont des ratios -> * 100
- Met a jour le default de 0.12 vers 12.00

Revision ID: fix_coeff_fg_unit
Revises: pieces_jointes_devis
Create Date: 2026-02-08
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fix_coeff_fg_unit"
down_revision = "pieces_jointes_devis"
branch_labels = None
depends_on = None


def upgrade():
    # 1. Convertir les donnees existantes: les valeurs < 1 sont des ratios
    #    (ex: 0.12 -> 12.00). Les valeurs >= 1 sont deja en pourcentage.
    op.execute(
        "UPDATE devis SET coeff_frais_generaux = coeff_frais_generaux * 100 "
        "WHERE coeff_frais_generaux < 1"
    )

    # 2. Changer le type de la colonne et le default
    op.alter_column(
        "devis",
        "coeff_frais_generaux",
        type_=sa.Numeric(5, 2),
        server_default="12.00",
        existing_nullable=False,
    )


def downgrade():
    # 1. Revenir au type Numeric(5,4) avec default 0.12
    op.alter_column(
        "devis",
        "coeff_frais_generaux",
        type_=sa.Numeric(5, 4),
        server_default="0.12",
        existing_nullable=False,
    )

    # 2. Reconvertir les pourcentages en ratios
    op.execute(
        "UPDATE devis SET coeff_frais_generaux = coeff_frais_generaux / 100 "
        "WHERE coeff_frais_generaux >= 1"
    )
