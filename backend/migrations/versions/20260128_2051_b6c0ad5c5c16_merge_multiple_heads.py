"""merge_multiple_heads

Revision ID: b6c0ad5c5c16
Revises: 20260124_0002, 20260125_0001, 20260129_0001
Create Date: 2026-01-28 20:51:44.283674+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b6c0ad5c5c16'
down_revision: Union[str, None] = ('20260124_0002', '20260125_0001', '20260129_0001')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
