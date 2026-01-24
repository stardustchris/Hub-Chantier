"""Schema pour le module Logistique - Gestion du Materiel.

Revision ID: 0003
Revises: 0002
Create Date: 2026-01-24 16:00:00.000000

Module: Logistique (CDC Section 11 - LOG-01 a LOG-18)
Fonctionnalites couvertes:
- LOG-01: Referentiel materiel (Admin uniquement)
- LOG-02: Fiche ressource (nom, code, photo, couleur, plage horaire)
- LOG-03 a LOG-06: Planning par ressource, navigation, axe horaire, blocs colores
- LOG-07 a LOG-09: Demande de reservation, selection chantier/creneau
- LOG-10: Option validation N+1 par ressource
- LOG-11, LOG-12: Workflow validation et statuts
- LOG-13 a LOG-15: Notifications (infrastructure separee)
- LOG-16: Motif de refus
- LOG-17: Detection conflits
- LOG-18: Historique par ressource

Regles metier:
- Une ressource appartient a l'entreprise (pas de FK vers chantier)
- Une reservation est liee a une ressource ET un chantier
- Workflow: demandeur -> valideur (N+1) -> statut mis a jour
- Possibilite de conflit si creneau deja reserve

Types de ressources (Greg Constructions):
- Engins de levage: Grue mobile, Manitou, Nacelle (N+1 requis)
- Engins de terrassement: Mini-pelle, Pelleteuse (N+1 requis)
- Vehicules: Camion benne, Fourgon (Validation optionnelle)
- Gros outillage: Betonniere, Vibrateur (Validation optionnelle)
- Equipements: Echafaudage, Etais, Banches (N+1 requis)
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
    """Creer les tables pour le module Logistique."""

    # ==========================================================================
    # TABLE: ressources
    # Referentiel du materiel de l'entreprise (LOG-01, LOG-02)
    # ==========================================================================
    op.create_table(
        'ressources',
        # Identifiant
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),

        # Identification (LOG-02)
        sa.Column('code', sa.String(20), nullable=False, unique=True),
        sa.Column('nom', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),

        # Categorie/Type de ressource
        # Valeurs: levage, terrassement, vehicule, outillage, equipement
        sa.Column('type_ressource', sa.String(50), nullable=False),

        # Identification visuelle (LOG-02)
        sa.Column('photo_url', sa.String(500), nullable=True),
        sa.Column('couleur', sa.String(7), nullable=False, server_default='#3498DB'),

        # Plage horaire par defaut (LOG-05) - Format HH:MM
        sa.Column('plage_horaire_debut', sa.String(5), nullable=False, server_default='08:00'),
        sa.Column('plage_horaire_fin', sa.String(5), nullable=False, server_default='18:00'),

        # Option validation N+1 (LOG-10)
        # True = demande doit etre validee par chef/conducteur
        # False = reservation directe
        sa.Column('validation_requise', sa.Boolean(), nullable=False, server_default='true'),

        # Statut
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),

        # Soft delete (RGPD compliant)
        sa.Column('deleted_at', sa.DateTime(), nullable=True),

        # Contraintes
        sa.PrimaryKeyConstraint('id'),

        # Arguments de table
        comment='Referentiel materiel de l entreprise (LOG-01, LOG-02)'
    )

    # Index pour recherches frequentes
    op.create_index('ix_ressources_code', 'ressources', ['code'], unique=True)
    op.create_index('ix_ressources_type', 'ressources', ['type_ressource'])
    op.create_index('ix_ressources_active', 'ressources', ['is_active', 'deleted_at'])

    # ==========================================================================
    # TABLE: reservations
    # Reservations de ressources par chantier (LOG-07 a LOG-12, LOG-16 a LOG-18)
    # ==========================================================================
    op.create_table(
        'reservations',
        # Identifiant
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),

        # Relations obligatoires
        # Ressource reservee
        sa.Column('ressource_id', sa.Integer(), sa.ForeignKey('ressources.id', ondelete='CASCADE'), nullable=False),
        # Chantier d'utilisation (LOG-08)
        sa.Column('chantier_id', sa.Integer(), sa.ForeignKey('chantiers.id', ondelete='CASCADE'), nullable=False),
        # Demandeur (qui fait la demande)
        sa.Column('demandeur_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=False),

        # Valideur (qui valide/refuse) - null si pas encore traite ou validation non requise
        sa.Column('valideur_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),

        # Creneau de reservation (LOG-09)
        sa.Column('date_debut', sa.Date(), nullable=False),
        sa.Column('date_fin', sa.Date(), nullable=False),  # Permet reservations multi-jours
        sa.Column('heure_debut', sa.String(5), nullable=False),  # Format HH:MM
        sa.Column('heure_fin', sa.String(5), nullable=False),    # Format HH:MM

        # Statut de la reservation (LOG-11, LOG-12)
        # Valeurs: en_attente (jaune), validee (vert), refusee (rouge), annulee
        sa.Column('statut', sa.String(20), nullable=False, server_default='en_attente'),

        # Motif de refus (LOG-16) - rempli si statut = refusee
        sa.Column('motif_refus', sa.Text(), nullable=True),

        # Note/commentaire du demandeur
        sa.Column('note', sa.Text(), nullable=True),

        # Horodatages des actions
        sa.Column('validated_at', sa.DateTime(), nullable=True),
        sa.Column('refused_at', sa.DateTime(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),

        # Timestamps
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),

        # Contraintes
        sa.PrimaryKeyConstraint('id'),

        # Contrainte de coherence: date_fin >= date_debut
        sa.CheckConstraint('date_fin >= date_debut', name='ck_reservation_dates'),

        # Arguments de table
        comment='Reservations de ressources par chantier (LOG-07 a LOG-18)'
    )

    # Index pour les recherches frequentes
    # Planning par ressource (LOG-03, LOG-18)
    op.create_index('ix_reservations_ressource_id', 'reservations', ['ressource_id'])
    op.create_index('ix_reservations_ressource_dates', 'reservations', ['ressource_id', 'date_debut', 'date_fin'])

    # Planning par chantier
    op.create_index('ix_reservations_chantier_id', 'reservations', ['chantier_id'])
    op.create_index('ix_reservations_chantier_dates', 'reservations', ['chantier_id', 'date_debut'])

    # Reservations par demandeur/valideur
    op.create_index('ix_reservations_demandeur_id', 'reservations', ['demandeur_id'])
    op.create_index('ix_reservations_valideur_id', 'reservations', ['valideur_id'])

    # Recherche par statut (pour liste des demandes en attente)
    op.create_index('ix_reservations_statut', 'reservations', ['statut'])
    op.create_index('ix_reservations_statut_ressource', 'reservations', ['statut', 'ressource_id'])

    # Index pour detection de conflits (LOG-17)
    # Requete typique: trouver les reservations qui chevauchent un creneau donne
    op.create_index(
        'ix_reservations_conflit',
        'reservations',
        ['ressource_id', 'statut', 'date_debut', 'date_fin', 'heure_debut', 'heure_fin']
    )

    # ==========================================================================
    # TABLE: historique_reservations
    # Journal des actions sur les reservations (LOG-18)
    # ==========================================================================
    op.create_table(
        'historique_reservations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),

        # Reservation concernee
        sa.Column('reservation_id', sa.Integer(), sa.ForeignKey('reservations.id', ondelete='CASCADE'), nullable=False),

        # Action effectuee
        # Valeurs: created, validated, refused, cancelled, modified
        sa.Column('action', sa.String(50), nullable=False),

        # Utilisateur ayant effectue l'action
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),

        # Details de l'action (JSON pour flexibilite)
        sa.Column('details', sa.JSON(), nullable=True),

        # Timestamp
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),

        sa.PrimaryKeyConstraint('id'),
        comment='Historique des actions sur les reservations (LOG-18)'
    )

    # Index pour l'historique
    op.create_index('ix_historique_reservations_reservation_id', 'historique_reservations', ['reservation_id'])
    op.create_index('ix_historique_reservations_user_id', 'historique_reservations', ['user_id'])
    op.create_index('ix_historique_reservations_action', 'historique_reservations', ['action'])
    op.create_index('ix_historique_reservations_created_at', 'historique_reservations', ['created_at'])


def downgrade() -> None:
    """Supprimer les tables du module Logistique."""

    # Supprimer les index de historique_reservations
    op.drop_index('ix_historique_reservations_created_at')
    op.drop_index('ix_historique_reservations_action')
    op.drop_index('ix_historique_reservations_user_id')
    op.drop_index('ix_historique_reservations_reservation_id')

    # Supprimer la table historique_reservations
    op.drop_table('historique_reservations')

    # Supprimer les index de reservations
    op.drop_index('ix_reservations_conflit')
    op.drop_index('ix_reservations_statut_ressource')
    op.drop_index('ix_reservations_statut')
    op.drop_index('ix_reservations_valideur_id')
    op.drop_index('ix_reservations_demandeur_id')
    op.drop_index('ix_reservations_chantier_dates')
    op.drop_index('ix_reservations_chantier_id')
    op.drop_index('ix_reservations_ressource_dates')
    op.drop_index('ix_reservations_ressource_id')

    # Supprimer la table reservations
    op.drop_table('reservations')

    # Supprimer les index de ressources
    op.drop_index('ix_ressources_active')
    op.drop_index('ix_ressources_type')
    op.drop_index('ix_ressources_code')

    # Supprimer la table ressources
    op.drop_table('ressources')
