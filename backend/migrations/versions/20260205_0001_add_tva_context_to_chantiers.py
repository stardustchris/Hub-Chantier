"""add_tva_context_to_chantiers

DEV-TVA: Ajoute les champs contexte TVA au modele chantier pour
permettre le pre-remplissage intelligent du taux TVA par defaut
lors de la creation de devis.

Revision ID: tva_context_chantier_001
Revises: pennylane_inbound_001
Create Date: 2026-02-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'tva_context_chantier_001'
down_revision = 'pennylane_inbound_001'
branch_labels = None
depends_on = None


def upgrade():
    # DEV-TVA: Contexte TVA pour pre-remplissage taux devis
    op.add_column('chantiers', sa.Column(
        'type_travaux', sa.String(length=50), nullable=True,
        comment='renovation, renovation_energetique, construction_neuve'
    ))
    op.add_column('chantiers', sa.Column(
        'batiment_plus_2ans', sa.Boolean(), nullable=True,
        comment='Batiment acheve depuis plus de 2 ans'
    ))
    op.add_column('chantiers', sa.Column(
        'usage_habitation', sa.Boolean(), nullable=True,
        comment='Immeuble affecte a l habitation'
    ))


def downgrade():
    op.drop_column('chantiers', 'usage_habitation')
    op.drop_column('chantiers', 'batiment_plus_2ans')
    op.drop_column('chantiers', 'type_travaux')
