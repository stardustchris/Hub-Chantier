"""Fix devis coeff_frais_generaux default from 12.00 to 19.00.

BUG CRITIQUE: Le default SQLAlchemy du champ devis.coeff_frais_generaux
etait 12.00 alors que la valeur correcte est 19.00 (coherent avec
ConfigurationEntreprise et calcul_financier.py).

Cette migration :
1. Change le server_default de 12.00 a 19.00
2. Met a jour les devis brouillon qui ont 12.00 (valeur erronee)

Les devis non-brouillon ne sont PAS modifies car ils ont ete
potentiellement valides/envoyes avec cette valeur.

Revision ID: 20260211_0004
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = "20260211_0004"
down_revision = "20260211_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Corriger le server_default pour les futurs INSERT
    op.alter_column(
        "devis",
        "coeff_frais_generaux",
        server_default="19.00",
    )

    # 2. Corriger les devis brouillon existants avec l'ancien default 12.00
    op.execute(
        sa.text(
            "UPDATE devis SET coeff_frais_generaux = 19.00 "
            "WHERE coeff_frais_generaux = 12.00 AND statut = 'brouillon'"
        )
    )


def downgrade() -> None:
    op.alter_column(
        "devis",
        "coeff_frais_generaux",
        server_default="12.00",
    )
