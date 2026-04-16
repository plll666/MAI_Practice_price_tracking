"""merge multiple heads

Revision ID: ac468089755c
Revises: d950766e9e0b
Create Date: 2026-04-13 13:13:57.958113

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac468089755c'
down_revision: Union[str, Sequence[str], None] = 'd950766e9e0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
