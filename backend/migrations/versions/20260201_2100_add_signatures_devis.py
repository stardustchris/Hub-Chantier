"""DEV-14: Add signatures_devis table for electronic signatures.

Signature electronique client conforme eIDAS (signature simple).
Tracabilite complete : horodatage, IP, user-agent, hash SHA-512 du document.

Revision ID: signatures_devis_001
Revises: a082c2b07225
Create Date: 2026-02-01 21:00:00.000000+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'signatures_devis_001'
down_revision: Union[str, None] = 'a082c2b07225'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'signatures_devis',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            'devis_id',
            sa.Integer(),
            sa.ForeignKey('devis.id', ondelete='CASCADE'),
            nullable=False,
            unique=True,
        ),

        # Type de signature
        sa.Column(
            'type_signature',
            sa.Enum(
                'dessin_tactile', 'upload_scan', 'nom_prenom',
                name='signature_devis_type_enum',
                native_enum=False,
            ),
            nullable=False,
        ),

        # Identite du signataire
        sa.Column('signataire_nom', sa.String(200), nullable=False),
        sa.Column('signataire_email', sa.String(255), nullable=False),
        sa.Column('signataire_telephone', sa.String(30), nullable=True),

        # Donnees de signature
        sa.Column('signature_data', sa.Text(), nullable=False),

        # Tracabilite eIDAS
        sa.Column('ip_adresse', sa.String(45), nullable=False),
        sa.Column('user_agent', sa.String(500), nullable=False),
        sa.Column('horodatage', sa.DateTime(), nullable=False),

        # Integrite document (SHA-512 = 128 hex chars)
        sa.Column('hash_document', sa.String(128), nullable=False),

        # Etat
        sa.Column('valide', sa.Boolean(), nullable=False, server_default=sa.text('true')),

        # Revocation
        sa.Column('revoquee_at', sa.DateTime(), nullable=True),
        sa.Column(
            'revoquee_par',
            sa.Integer(),
            sa.ForeignKey('users.id', ondelete='SET NULL'),
            nullable=True,
        ),
        sa.Column('motif_revocation', sa.Text(), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),

        # Contraintes CHECK
        sa.CheckConstraint(
            "length(hash_document) = 128",
            name='check_signatures_devis_hash_sha512',
        ),
        sa.CheckConstraint(
            "length(ip_adresse) >= 7",
            name='check_signatures_devis_ip_non_vide',
        ),
        sa.CheckConstraint(
            "(revoquee_at IS NULL) OR (motif_revocation IS NOT NULL AND motif_revocation != '')",
            name='check_signatures_devis_revocation_coherente',
        ),
        sa.CheckConstraint(
            "(revoquee_at IS NULL) OR (valide = false)",
            name='check_signatures_devis_revoquee_invalide',
        ),
    )

    # Index explicites
    op.create_index(
        'ix_signatures_devis_devis_id',
        'signatures_devis',
        ['devis_id'],
    )
    op.create_index(
        'ix_signatures_devis_devis_valide',
        'signatures_devis',
        ['devis_id', 'valide'],
    )
    op.create_index(
        'ix_signatures_devis_horodatage',
        'signatures_devis',
        ['horodatage'],
    )


def downgrade() -> None:
    op.drop_index('ix_signatures_devis_horodatage')
    op.drop_index('ix_signatures_devis_devis_valide')
    op.drop_index('ix_signatures_devis_devis_id')
    op.drop_table('signatures_devis')
