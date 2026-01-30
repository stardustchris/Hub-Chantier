"""Add heures_prevues to affectations

Revision ID: 45fbfeb64662
Revises: 670f48881d6d
Create Date: 2026-01-30 21:14:54.384687+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '45fbfeb64662'
down_revision: Union[str, None] = '670f48881d6d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ajouter la colonne heures_prevues avec une valeur par defaut de 8.0
    op.add_column(
        'affectations',
        sa.Column('heures_prevues', sa.Float(), nullable=False, server_default='8.0')
    )


def downgrade() -> None:
    # Supprimer la colonne heures_prevues
    op.drop_column('affectations', 'heures_prevues')
