"""Create logistique module schema (ressources and reservations).

Revision ID: 0003
Revises: 0002
Create Date: 2026-01-24 16:00:00.000000

LOG-01: Référentiel matériel
LOG-02: Fiche ressource
LOG-07 à LOG-18: Réservations et workflow
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0003'
down_revision: Union[str, None] = '0002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create ressources and reservations tables with FK and CHECK constraints."""

    # ==========================================================================
    # Table: ressources (LOG-01, LOG-02)
    # ==========================================================================
    op.create_table(
        'ressources',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nom', sa.String(200), nullable=False),
        sa.Column('code', sa.String(20), nullable=False),
        sa.Column('categorie', sa.String(50), nullable=False),
        sa.Column('photo_url', sa.String(500), nullable=True),
        sa.Column('couleur', sa.String(7), nullable=False, server_default='#3B82F6'),
        sa.Column('heure_debut_defaut', sa.Time(), nullable=False, server_default='08:00:00'),
        sa.Column('heure_fin_defaut', sa.Time(), nullable=False, server_default='18:00:00'),
        sa.Column('validation_requise', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('actif', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        # FK: created_by -> users.id
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        # CHECK: heure_fin_defaut > heure_debut_defaut
        sa.CheckConstraint(
            'heure_fin_defaut > heure_debut_defaut',
            name='check_ressources_plage_horaire'
        ),
    )

    # Indexes for ressources
    op.create_index('ix_ressources_code', 'ressources', ['code'], unique=True)
    op.create_index('ix_ressources_categorie', 'ressources', ['categorie'])
    op.create_index('ix_ressources_actif', 'ressources', ['actif'])
    op.create_index('ix_ressources_categorie_actif', 'ressources', ['categorie', 'actif'])

    # ==========================================================================
    # Table: reservations (LOG-07 à LOG-18)
    # ==========================================================================
    op.create_table(
        'reservations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ressource_id', sa.Integer(), nullable=False),
        sa.Column('chantier_id', sa.Integer(), nullable=False),
        sa.Column('demandeur_id', sa.Integer(), nullable=False),
        sa.Column('date_reservation', sa.Date(), nullable=False),
        sa.Column('heure_debut', sa.Time(), nullable=False),
        sa.Column('heure_fin', sa.Time(), nullable=False),
        sa.Column('statut', sa.String(20), nullable=False, server_default='en_attente'),
        sa.Column('motif_refus', sa.Text(), nullable=True),
        sa.Column('commentaire', sa.Text(), nullable=True),
        sa.Column('valideur_id', sa.Integer(), nullable=True),
        sa.Column('validated_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        # FK: ressource_id -> ressources.id
        sa.ForeignKeyConstraint(
            ['ressource_id'], ['ressources.id'],
            ondelete='RESTRICT',
            name='fk_reservations_ressource'
        ),
        # FK: chantier_id -> chantiers.id
        sa.ForeignKeyConstraint(
            ['chantier_id'], ['chantiers.id'],
            ondelete='RESTRICT',
            name='fk_reservations_chantier'
        ),
        # FK: demandeur_id -> users.id
        sa.ForeignKeyConstraint(
            ['demandeur_id'], ['users.id'],
            ondelete='RESTRICT',
            name='fk_reservations_demandeur'
        ),
        # FK: valideur_id -> users.id
        sa.ForeignKeyConstraint(
            ['valideur_id'], ['users.id'],
            ondelete='SET NULL',
            name='fk_reservations_valideur'
        ),
        # CHECK: heure_fin > heure_debut
        sa.CheckConstraint(
            'heure_fin > heure_debut',
            name='check_reservations_plage_horaire'
        ),
    )

    # Indexes for reservations
    op.create_index('ix_reservations_ressource_id', 'reservations', ['ressource_id'])
    op.create_index('ix_reservations_chantier_id', 'reservations', ['chantier_id'])
    op.create_index('ix_reservations_demandeur_id', 'reservations', ['demandeur_id'])
    op.create_index('ix_reservations_date_reservation', 'reservations', ['date_reservation'])
    op.create_index('ix_reservations_statut', 'reservations', ['statut'])

    # Composite indexes for common queries
    op.create_index(
        'ix_reservations_ressource_date',
        'reservations',
        ['ressource_id', 'date_reservation']
    )
    op.create_index(
        'ix_reservations_statut_date',
        'reservations',
        ['statut', 'date_reservation']
    )
    op.create_index(
        'ix_reservations_chantier_date',
        'reservations',
        ['chantier_id', 'date_reservation']
    )
    op.create_index(
        'ix_reservations_demandeur_statut',
        'reservations',
        ['demandeur_id', 'statut']
    )
    # Index for conflict detection (LOG-17)
    op.create_index(
        'ix_reservations_ressource_statut_date',
        'reservations',
        ['ressource_id', 'statut', 'date_reservation']
    )


def downgrade() -> None:
    """Drop ressources and reservations tables."""

    # Drop indexes for reservations
    op.drop_index('ix_reservations_ressource_statut_date')
    op.drop_index('ix_reservations_demandeur_statut')
    op.drop_index('ix_reservations_chantier_date')
    op.drop_index('ix_reservations_statut_date')
    op.drop_index('ix_reservations_ressource_date')
    op.drop_index('ix_reservations_statut')
    op.drop_index('ix_reservations_date_reservation')
    op.drop_index('ix_reservations_demandeur_id')
    op.drop_index('ix_reservations_chantier_id')
    op.drop_index('ix_reservations_ressource_id')

    # Drop reservations table
    op.drop_table('reservations')

    # Drop indexes for ressources
    op.drop_index('ix_ressources_categorie_actif')
    op.drop_index('ix_ressources_actif')
    op.drop_index('ix_ressources_categorie')
    op.drop_index('ix_ressources_code')

    # Drop ressources table
    op.drop_table('ressources')
