"""Ajout table pieces_jointes_devis.

DEV-07: Pieces jointes pour devis.

Revision ID: pieces_jointes_devis
Revises: devis_generator_fields
Create Date: 2026-02-05
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'pieces_jointes_devis'
down_revision = 'devis_generator_fields'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'pieces_jointes_devis',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('devis_id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=True),
        sa.Column('lot_devis_id', sa.Integer(), nullable=True),
        sa.Column('ligne_devis_id', sa.Integer(), nullable=True),
        sa.Column('visible_client', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('ordre', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('nom_fichier', sa.String(255), nullable=True),
        sa.Column('type_fichier', sa.String(50), nullable=True),
        sa.Column('taille_octets', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(['devis_id'], ['devis.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['lot_devis_id'], ['lots_devis.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['ligne_devis_id'], ['lignes_devis.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('devis_id', 'document_id', name='uq_devis_document'),
    )
    op.create_index('ix_pieces_jointes_devis_id', 'pieces_jointes_devis', ['devis_id'])
    op.create_index('ix_pieces_jointes_devis_ordre', 'pieces_jointes_devis', ['devis_id', 'ordre'])


def downgrade():
    op.drop_index('ix_pieces_jointes_devis_ordre')
    op.drop_index('ix_pieces_jointes_devis_id')
    op.drop_table('pieces_jointes_devis')
