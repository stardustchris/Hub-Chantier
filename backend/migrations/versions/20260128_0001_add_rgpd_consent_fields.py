"""add_rgpd_consent_fields

Revision ID: 20260128_0001
Revises:
Create Date: 2026-01-28

Ajoute les champs de consentement RGPD à la table users
conformément à l'Article 7 RGPD (preuve du consentement).

Cette migration est créée de manière autonome (pas de down_revision)
car elle s'applique à un schéma existant et peut être appliquée
indépendamment des autres migrations.

Champs ajoutés :
- consent_geolocation: bool (consentement géolocalisation)
- consent_notifications: bool (consentement notifications push)
- consent_analytics: bool (consentement analytics/statistiques)
- consent_timestamp: datetime (date/heure du consentement)
- consent_ip_address: str (adresse IP lors du consentement)
- consent_user_agent: str (user agent lors du consentement)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '20260128_0001'
down_revision = None  # Migration autonome
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Ajoute les champs de consentement RGPD à la table users."""

    conn = op.get_bind()
    inspector = inspect(conn)

    # Vérifier si la table users existe
    if 'users' in inspector.get_table_names():
        existing_columns = [c['name'] for c in inspector.get_columns('users')]

        # Ajouter les champs de consentement seulement s'ils n'existent pas
        if 'consent_geolocation' not in existing_columns:
            op.add_column('users', sa.Column('consent_geolocation', sa.Boolean(), nullable=False, server_default='false'))
        if 'consent_notifications' not in existing_columns:
            op.add_column('users', sa.Column('consent_notifications', sa.Boolean(), nullable=False, server_default='false'))
        if 'consent_analytics' not in existing_columns:
            op.add_column('users', sa.Column('consent_analytics', sa.Boolean(), nullable=False, server_default='false'))

        # Ajouter les champs de traçabilité RGPD
        if 'consent_timestamp' not in existing_columns:
            op.add_column('users', sa.Column('consent_timestamp', sa.DateTime(), nullable=True))
        if 'consent_ip_address' not in existing_columns:
            op.add_column('users', sa.Column('consent_ip_address', sa.String(45), nullable=True))  # IPv6 max 45 chars
        if 'consent_user_agent' not in existing_columns:
            op.add_column('users', sa.Column('consent_user_agent', sa.String(500), nullable=True))

        # Index pour requêtes fréquentes (vérifier si existe déjà)
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('users')]
        if 'idx_users_consent_timestamp' not in existing_indexes:
            op.create_index('idx_users_consent_timestamp', 'users', ['consent_timestamp'])


def downgrade() -> None:
    """Retire les champs de consentement RGPD."""

    conn = op.get_bind()
    inspector = inspect(conn)

    if 'users' in inspector.get_table_names():
        existing_columns = [c['name'] for c in inspector.get_columns('users')]
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('users')]

        # Supprimer l'index si existe
        if 'idx_users_consent_timestamp' in existing_indexes:
            op.drop_index('idx_users_consent_timestamp', table_name='users')

        # Supprimer les colonnes si existent
        if 'consent_user_agent' in existing_columns:
            op.drop_column('users', 'consent_user_agent')
        if 'consent_ip_address' in existing_columns:
            op.drop_column('users', 'consent_ip_address')
        if 'consent_timestamp' in existing_columns:
            op.drop_column('users', 'consent_timestamp')
        if 'consent_analytics' in existing_columns:
            op.drop_column('users', 'consent_analytics')
        if 'consent_notifications' in existing_columns:
            op.drop_column('users', 'consent_notifications')
        if 'consent_geolocation' in existing_columns:
            op.drop_column('users', 'consent_geolocation')
