"""add_maitre_ouvrage_to_chantiers

Revision ID: 20260130_0001
Revises: 20260128_2051_b6c0ad5c5c16
Create Date: 2026-01-30

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260130_0001'
down_revision = 'b6c0ad5c5c16'
branch_labels = None
depends_on = None


def upgrade():
    # Ajouter la colonne maitre_ouvrage
    op.add_column('chantiers', sa.Column('maitre_ouvrage', sa.String(length=200), nullable=True))

    # Migrer les données existantes de contact_nom vers maitre_ouvrage
    op.execute("""
        UPDATE chantiers
        SET maitre_ouvrage = contact_nom
        WHERE contact_nom IS NOT NULL
    """)


def downgrade():
    # Supprimer la colonne maitre_ouvrage
    op.drop_column('chantiers', 'maitre_ouvrage')
