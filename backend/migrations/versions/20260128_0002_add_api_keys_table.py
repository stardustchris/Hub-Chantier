"""add_api_keys_table

Revision ID: 20260128_0002
Revises: 20260128_0001
Create Date: 2026-01-28

Ajoute la table api_keys pour l'authentification via clés API de l'API publique v1.

Cette table stocke les clés API des utilisateurs avec :
- Hash SHA256 sécurisé (jamais de secret en clair)
- Préfixe pour affichage (hbc_xxxxxxxx...)
- Scopes (permissions)
- Rate limiting par clé
- Traçabilité (last_used_at, expires_at)

Conformité sécurité :
- Stockage hash SHA256 uniquement (OWASP)
- Foreign Key CASCADE pour suppression utilisateur
- Index optimisés pour authentification rapide
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '20260128_0002'
down_revision = '20260128_0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Crée la table api_keys avec tous les index."""

    conn = op.get_bind()
    inspector = inspect(conn)

    # Vérifier si la table existe déjà
    if 'api_keys' not in inspector.get_table_names():
        # Créer la table api_keys
        op.create_table(
            'api_keys',
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
            sa.Column('key_hash', sa.String(64), unique=True, nullable=False,
                     comment='SHA256 hash du secret API (jamais stocké en clair)'),
            sa.Column('key_prefix', sa.String(8), nullable=False,
                     comment='Préfixe pour affichage (hbc_xxxx...)'),
            sa.Column('user_id', sa.Integer(), nullable=False,
                     comment='Utilisateur propriétaire de la clé'),
            sa.Column('nom', sa.String(255), nullable=False,
                     comment='Nom descriptif de la clé'),
            sa.Column('description', sa.Text(), nullable=True,
                     comment='Description détaillée (optionnel)'),
            sa.Column('scopes', postgresql.ARRAY(sa.String()), nullable=False,
                     server_default="ARRAY['read']::text[]",
                     comment='Permissions accordées (read, write, admin)'),
            sa.Column('rate_limit_per_hour', sa.Integer(), nullable=False,
                     server_default='1000',
                     comment='Limite de requêtes par heure'),
            sa.Column('is_active', sa.Boolean(), nullable=False,
                     server_default='true',
                     comment='Clé active ou révoquée'),
            sa.Column('last_used_at', sa.DateTime(), nullable=True,
                     comment='Dernière utilisation pour audit'),
            sa.Column('expires_at', sa.DateTime(), nullable=True,
                     comment='Date d\'expiration (NULL = jamais)'),
            sa.Column('created_at', sa.DateTime(), nullable=False,
                     server_default=sa.func.now(),
                     comment='Date de création'),

            # Foreign Key vers users avec CASCADE delete
            sa.ForeignKeyConstraint(['user_id'], ['users.id'],
                                  name='fk_api_keys_user_id',
                                  ondelete='CASCADE'),

            # Contraintes
            sa.UniqueConstraint('key_hash', name='uq_api_keys_key_hash'),
            sa.PrimaryKeyConstraint('id', name='pk_api_keys'),
        )

        # Index pour authentification (très fréquent, doit être ultra-rapide)
        op.create_index('idx_api_keys_key_hash', 'api_keys', ['key_hash'], unique=True)

        # Index pour lister les clés d'un utilisateur
        op.create_index('idx_api_keys_user_id', 'api_keys', ['user_id'])

        # Index partiel pour clés actives (optimisation requêtes)
        op.create_index(
            'idx_api_keys_active',
            'api_keys',
            ['is_active'],
            postgresql_where=sa.text('is_active = true')
        )

        # Index pour audit/cleanup des clés expirées
        op.create_index('idx_api_keys_expires_at', 'api_keys', ['expires_at'])


def downgrade() -> None:
    """Supprime la table api_keys et tous ses index."""

    conn = op.get_bind()
    inspector = inspect(conn)

    if 'api_keys' in inspector.get_table_names():
        # Supprimer les index d'abord
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('api_keys')]

        if 'idx_api_keys_expires_at' in existing_indexes:
            op.drop_index('idx_api_keys_expires_at', table_name='api_keys')
        if 'idx_api_keys_active' in existing_indexes:
            op.drop_index('idx_api_keys_active', table_name='api_keys')
        if 'idx_api_keys_user_id' in existing_indexes:
            op.drop_index('idx_api_keys_user_id', table_name='api_keys')
        if 'idx_api_keys_key_hash' in existing_indexes:
            op.drop_index('idx_api_keys_key_hash', table_name='api_keys')

        # Supprimer la table
        op.drop_table('api_keys')
