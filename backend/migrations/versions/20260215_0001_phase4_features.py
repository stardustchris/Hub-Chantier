"""Phase 4: coefficient productivite, charges par categorie, alertes budget, commentaire devis.

Revision ID: 20260215_0001
Revises: (last migration)
Create Date: 2026-02-15

"""
from alembic import op
import sqlalchemy as sa

revision = '20260215_0001'
down_revision = '20260211_0004'
branch_labels = None
depends_on = None


def upgrade():
    # 4.4: Commentaire libre devis
    op.add_column('devis', sa.Column('commentaire', sa.Text(), nullable=True))

    # 4.1: Coefficient productivite
    op.add_column('configuration_entreprise', sa.Column('coeff_productivite', sa.Numeric(5, 3), nullable=False, server_default='1.000'))
    op.add_column('devis', sa.Column('coeff_productivite', sa.Numeric(5, 3), nullable=True))

    # 4.2: Granularite charges par categorie
    op.add_column('configuration_entreprise', sa.Column('coeff_charges_ouvrier', sa.Numeric(5, 3), nullable=True))
    op.add_column('configuration_entreprise', sa.Column('coeff_charges_etam', sa.Numeric(5, 3), nullable=True))
    op.add_column('configuration_entreprise', sa.Column('coeff_charges_cadre', sa.Numeric(5, 3), nullable=True))

    # 4.3: Alertes budget configurables
    op.add_column('configuration_entreprise', sa.Column('seuil_alerte_budget_pct', sa.Numeric(5, 2), nullable=False, server_default='80'))
    op.add_column('configuration_entreprise', sa.Column('seuil_alerte_budget_critique_pct', sa.Numeric(5, 2), nullable=False, server_default='95'))


def downgrade():
    op.drop_column('devis', 'commentaire')
    op.drop_column('devis', 'coeff_productivite')
    op.drop_column('configuration_entreprise', 'coeff_productivite')
    op.drop_column('configuration_entreprise', 'coeff_charges_ouvrier')
    op.drop_column('configuration_entreprise', 'coeff_charges_etam')
    op.drop_column('configuration_entreprise', 'coeff_charges_cadre')
    op.drop_column('configuration_entreprise', 'seuil_alerte_budget_pct')
    op.drop_column('configuration_entreprise', 'seuil_alerte_budget_critique_pct')
