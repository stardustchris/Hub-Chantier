"""Migration convertir metier (string) vers metiers (JSON array).

Revision ID: 20260131_0001
Revises: 20260130_2114_45fbfeb64662
Create Date: 2026-01-31 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260131_0001'
down_revision = '45fbfeb64662'
branch_labels = None
depends_on = None


def upgrade():
    """
    Convertit le champ metier (string unique) en metiers (JSON array).

    Stratégie:
    1. Ajouter colonne metiers (JSON, nullable)
    2. Migrer les données: metiers = [metier] si metier existe
    3. Supprimer l'ancienne colonne metier

    Note: Utilise batch mode pour compatibilité SQLite (tests).
    """
    # 1. Ajouter la nouvelle colonne metiers (JSON)
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('metiers', sa.JSON(), nullable=True)
        )

    # 2. Migrer les données existantes
    # Convertir metier (string) -> metiers (array JSON)
    connection = op.get_bind()

    # Pour PostgreSQL, utiliser jsonb_build_array
    # Pour SQLite, utiliser json_array
    if connection.dialect.name == 'postgresql':
        connection.execute(
            sa.text("""
                UPDATE users
                SET metiers = jsonb_build_array(metier)
                WHERE metier IS NOT NULL AND metier != ''
            """)
        )
    else:  # SQLite
        connection.execute(
            sa.text("""
                UPDATE users
                SET metiers = json_array(metier)
                WHERE metier IS NOT NULL AND metier != ''
            """)
        )

    # 3. Supprimer l'ancienne colonne metier
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('metier')


def downgrade():
    """
    Revient au modèle avec metier (string unique).

    Stratégie:
    1. Ajouter colonne metier (String)
    2. Migrer les données: prendre le premier métier si plusieurs
    3. Supprimer la colonne metiers

    ATTENTION: Perte de données si un utilisateur a plusieurs métiers.
    """
    # 1. Re-créer la colonne metier
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('metier', sa.String(length=100), nullable=True)
        )

    # 2. Migrer les données (prendre le premier métier)
    connection = op.get_bind()

    if connection.dialect.name == 'postgresql':
        connection.execute(
            sa.text("""
                UPDATE users
                SET metier = metiers->>0
                WHERE metiers IS NOT NULL
                  AND jsonb_array_length(metiers) > 0
            """)
        )
    else:  # SQLite
        connection.execute(
            sa.text("""
                UPDATE users
                SET metier = json_extract(metiers, '$[0]')
                WHERE metiers IS NOT NULL
                  AND json_array_length(metiers) > 0
            """)
        )

    # 3. Supprimer la colonne metiers
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('metiers')
