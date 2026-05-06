"""add_telegram_settings_to_users

Revision ID: a1b2c3d4e5f6
Revises: 2bd51154469c
Create Date: 2026-05-04 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '2bd51154469c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('telegram_notifications_enabled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('email_notifications_enabled', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('telegram_linking_code', sa.String(6), nullable=True))
    op.add_column('users', sa.Column('telegram_linking_code_expires', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'telegram_linking_code_expires')
    op.drop_column('users', 'telegram_linking_code')
    op.drop_column('users', 'email_notifications_enabled')
    op.drop_column('users', 'telegram_notifications_enabled')
