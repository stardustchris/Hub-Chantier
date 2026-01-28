"""add_webhooks_and_event_logs

Revision ID: 20260129_0001
Revises: 20260128_0002
Create Date: 2026-01-29

Ajoute les tables pour l'architecture événementielle et les webhooks :
- webhooks : Configuration des webhooks (URL, événements, secret HMAC)
- webhook_deliveries : Historique des tentatives de livraison
- event_logs : Audit trail des événements (optionnel)

Conformité sécurité :
- Signatures HMAC-SHA256 pour webhooks
- Retry exponentiel configuré
- Désactivation automatique après échecs
- Foreign Key CASCADE pour suppression utilisateur
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = '20260129_0001'
down_revision = '20260128_0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Crée les tables webhooks, webhook_deliveries et event_logs."""

    conn = op.get_bind()
    inspector = inspect(conn)
    dialect_name = conn.dialect.name

    # Types compatibles SQLite/PostgreSQL
    if dialect_name == 'postgresql':
        id_type = postgresql.UUID(as_uuid=True)
        events_type = postgresql.ARRAY(sa.String())
        json_type = postgresql.JSONB()
    else:  # SQLite
        id_type = sa.String(36)  # UUID as string
        events_type = sa.Text()  # JSON array as text
        json_type = sa.Text()  # JSON as text

    # Table 1 : webhooks
    if 'webhooks' not in inspector.get_table_names():
        op.create_table(
            'webhooks',
            sa.Column('id', id_type, primary_key=True, nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False,
                     comment='Utilisateur propriétaire du webhook'),

            # Configuration
            sa.Column('url', sa.String(500), nullable=False,
                     comment='URL destination du webhook'),
            sa.Column('events', events_type, nullable=False,
                     comment='Patterns d\'événements à écouter (ex: chantier.*, heures.validated) - JSON pour SQLite'),
            sa.Column('secret', sa.String(64), nullable=False,
                     comment='Secret pour signatures HMAC-SHA256'),
            sa.Column('description', sa.Text(), nullable=True,
                     comment='Description du webhook'),

            # État
            sa.Column('is_active', sa.Boolean(), nullable=False,
                     server_default='true',
                     comment='Webhook actif ou désactivé'),
            sa.Column('last_triggered_at', sa.DateTime(), nullable=True,
                     comment='Dernière fois déclenché avec succès'),
            sa.Column('consecutive_failures', sa.Integer(), nullable=False,
                     server_default='0',
                     comment='Nombre d\'échecs consécutifs (auto-désactivation à 10)'),

            # Retry configuration
            sa.Column('retry_enabled', sa.Boolean(), nullable=False,
                     server_default='true',
                     comment='Retry automatique activé'),
            sa.Column('max_retries', sa.Integer(), nullable=False,
                     server_default='3',
                     comment='Nombre maximum de tentatives (retry exponentiel)'),

            # Timestamps
            sa.Column('created_at', sa.DateTime(), nullable=False,
                     server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(), nullable=False,
                     server_default=sa.func.now()),

            # Foreign Key vers users avec CASCADE
            sa.ForeignKeyConstraint(['user_id'], ['users.id'],
                                  name='fk_webhooks_user_id',
                                  ondelete='CASCADE'),

            sa.PrimaryKeyConstraint('id', name='pk_webhooks'),
        )

        # Index pour webhooks
        op.create_index('idx_webhooks_user_id', 'webhooks', ['user_id'])
        op.create_index(
            'idx_webhooks_active',
            'webhooks',
            ['is_active'],
            postgresql_where=sa.text('is_active = true')
        )

    # Table 2 : webhook_deliveries
    if 'webhook_deliveries' not in inspector.get_table_names():
        op.create_table(
            'webhook_deliveries',
            sa.Column('id', id_type, primary_key=True, nullable=False),
            sa.Column('webhook_id', id_type, nullable=False,
                     comment='Webhook concerné'),

            # Événement
            sa.Column('event_type', sa.String(100), nullable=False,
                     comment='Type d\'événement (ex: chantier.created)'),
            sa.Column('payload', json_type, nullable=False,
                     comment='Payload JSON de l\'événement'),

            # Résultat delivery
            sa.Column('status_code', sa.Integer(), nullable=True,
                     comment='Code HTTP de la réponse'),
            sa.Column('response_body', sa.Text(), nullable=True,
                     comment='Corps de la réponse (limité 1000 chars)'),
            sa.Column('success', sa.Boolean(), nullable=True,
                     comment='Livraison réussie (HTTP 2xx)'),
            sa.Column('error_message', sa.Text(), nullable=True,
                     comment='Message d\'erreur si échec'),

            # Timing
            sa.Column('delivered_at', sa.DateTime(), nullable=False,
                     server_default=sa.func.now(),
                     comment='Timestamp de la tentative'),
            sa.Column('response_time_ms', sa.Integer(), nullable=True,
                     comment='Temps de réponse en millisecondes'),

            # Retry
            sa.Column('attempt_number', sa.Integer(), nullable=False,
                     server_default='1',
                     comment='Numéro de tentative (1, 2, 3...)'),

            # Foreign Key vers webhooks avec CASCADE
            sa.ForeignKeyConstraint(['webhook_id'], ['webhooks.id'],
                                  name='fk_webhook_deliveries_webhook_id',
                                  ondelete='CASCADE'),

            sa.PrimaryKeyConstraint('id', name='pk_webhook_deliveries'),
        )

        # Index pour webhook_deliveries
        op.create_index('idx_deliveries_webhook_id', 'webhook_deliveries', ['webhook_id'])
        op.create_index('idx_deliveries_event_type', 'webhook_deliveries', ['event_type'])
        op.create_index('idx_deliveries_delivered_at', 'webhook_deliveries', ['delivered_at'])
        op.create_index('idx_deliveries_success', 'webhook_deliveries', ['success'])

        # Index partiel pour échecs (optimisation queries erreurs)
        op.create_index(
            'idx_failed_deliveries',
            'webhook_deliveries',
            ['webhook_id', 'delivered_at'],
            postgresql_where=sa.text('success = false')
        )

    # Table 3 : event_logs (audit trail optionnel)
    if 'event_logs' not in inspector.get_table_names():
        op.create_table(
            'event_logs',
            sa.Column('id', id_type, primary_key=True, nullable=False),
            sa.Column('event_type', sa.String(100), nullable=False,
                     comment='Type d\'événement (ex: chantier.created)'),
            sa.Column('aggregate_id', sa.String(100), nullable=True,
                     comment='ID de la ressource concernée (chantier_id, user_id, etc.)'),
            sa.Column('payload', json_type, nullable=False,
                     comment='Données complètes de l\'événement'),
            sa.Column('metadata', json_type, nullable=True,
                     comment='Métadonnées (user_id, ip_address, user_agent)'),
            sa.Column('occurred_at', sa.DateTime(), nullable=False,
                     server_default=sa.func.now(),
                     comment='Timestamp de l\'événement'),

            sa.PrimaryKeyConstraint('id', name='pk_event_logs'),
        )

        # Index pour event_logs
        op.create_index('idx_event_logs_type', 'event_logs', ['event_type'])
        op.create_index('idx_event_logs_aggregate', 'event_logs', ['aggregate_id'])
        op.create_index('idx_event_logs_occurred', 'event_logs', ['occurred_at'])


def downgrade() -> None:
    """Supprime les tables webhooks, webhook_deliveries et event_logs."""

    conn = op.get_bind()
    inspector = inspect(conn)

    # Supprimer dans l'ordre inverse (dépendances)

    # Table 3 : event_logs
    if 'event_logs' in inspector.get_table_names():
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('event_logs')]

        if 'idx_event_logs_occurred' in existing_indexes:
            op.drop_index('idx_event_logs_occurred', table_name='event_logs')
        if 'idx_event_logs_aggregate' in existing_indexes:
            op.drop_index('idx_event_logs_aggregate', table_name='event_logs')
        if 'idx_event_logs_type' in existing_indexes:
            op.drop_index('idx_event_logs_type', table_name='event_logs')

        op.drop_table('event_logs')

    # Table 2 : webhook_deliveries
    if 'webhook_deliveries' in inspector.get_table_names():
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('webhook_deliveries')]

        if 'idx_failed_deliveries' in existing_indexes:
            op.drop_index('idx_failed_deliveries', table_name='webhook_deliveries')
        if 'idx_deliveries_success' in existing_indexes:
            op.drop_index('idx_deliveries_success', table_name='webhook_deliveries')
        if 'idx_deliveries_delivered_at' in existing_indexes:
            op.drop_index('idx_deliveries_delivered_at', table_name='webhook_deliveries')
        if 'idx_deliveries_event_type' in existing_indexes:
            op.drop_index('idx_deliveries_event_type', table_name='webhook_deliveries')
        if 'idx_deliveries_webhook_id' in existing_indexes:
            op.drop_index('idx_deliveries_webhook_id', table_name='webhook_deliveries')

        op.drop_table('webhook_deliveries')

    # Table 1 : webhooks
    if 'webhooks' in inspector.get_table_names():
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('webhooks')]

        if 'idx_webhooks_active' in existing_indexes:
            op.drop_index('idx_webhooks_active', table_name='webhooks')
        if 'idx_webhooks_user_id' in existing_indexes:
            op.drop_index('idx_webhooks_user_id', table_name='webhooks')

        op.drop_table('webhooks')
