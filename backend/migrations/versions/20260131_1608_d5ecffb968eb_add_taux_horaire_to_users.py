"""add_taux_horaire_to_users

Revision ID: d5ecffb968eb
Revises: 20260131_0001
Create Date: 2026-01-31 16:08:12.688383+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5ecffb968eb'
down_revision: Union[str, None] = '20260131_0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Ajoute la colonne taux_horaire à la table users.

    Cette colonne stocke le taux horaire de l'employé pour le module financier (FIN-09).
    Numeric(8,2) permet de stocker jusqu'à 999999.99 (ex: 45.50 EUR/heure).
    """
    # Utiliser batch mode pour compatibilité SQLite
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('taux_horaire', sa.Numeric(precision=8, scale=2), nullable=True)
        )


def downgrade() -> None:
    """
    Supprime la colonne taux_horaire de la table users.
    """
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('taux_horaire')
