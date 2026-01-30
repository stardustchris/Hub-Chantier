"""Add password reset, invitation, and email verification columns

Revision ID: 670f48881d6d
Revises: 20260130_0001
Create Date: 2026-01-30 16:30:14.715654+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '670f48881d6d'
down_revision: Union[str, None] = '20260130_0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add password reset columns
    op.add_column('users', sa.Column('password_reset_token', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('password_reset_expires_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index('ix_users_password_reset_token', 'users', ['password_reset_token'])

    # Add invitation columns
    op.add_column('users', sa.Column('invitation_token', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('invitation_expires_at', sa.DateTime(timezone=True), nullable=True))
    op.create_index('ix_users_invitation_token', 'users', ['invitation_token'])

    # Add email verification columns
    op.add_column('users', sa.Column('email_verified_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('email_verification_token', sa.String(255), nullable=True))
    op.create_index('ix_users_email_verification_token', 'users', ['email_verification_token'])

    # Add account lockout columns
    op.add_column('users', sa.Column('failed_login_attempts', sa.Integer, nullable=False, server_default='0'))
    op.add_column('users', sa.Column('last_failed_login_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    # Remove account lockout columns
    op.drop_column('users', 'locked_until')
    op.drop_column('users', 'last_failed_login_at')
    op.drop_column('users', 'failed_login_attempts')

    # Remove email verification columns
    op.drop_index('ix_users_email_verification_token', table_name='users')
    op.drop_column('users', 'email_verification_token')
    op.drop_column('users', 'email_verified_at')

    # Remove invitation columns
    op.drop_index('ix_users_invitation_token', table_name='users')
    op.drop_column('users', 'invitation_expires_at')
    op.drop_column('users', 'invitation_token')

    # Remove password reset columns
    op.drop_index('ix_users_password_reset_token', table_name='users')
    op.drop_column('users', 'password_reset_expires_at')
    op.drop_column('users', 'password_reset_token')
