"""merge audit_log and taux_horaire heads

Revision ID: a082c2b07225
Revises: audit_log_immutability_001, d5ecffb968eb
Create Date: 2026-02-01 20:35:48.808657+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a082c2b07225'
down_revision: Union[str, None] = ('audit_log_immutability_001', 'd5ecffb968eb')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
