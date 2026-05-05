"""merge two heads

Revision ID: 2bd51154469c
Revises: c8535b0f3c07, f1a2b3c4d5e6
Create Date: 2026-04-30 17:15:53.736242

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2bd51154469c'
down_revision: Union[str, Sequence[str], None] = ('c8535b0f3c07', 'f1a2b3c4d5e6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
