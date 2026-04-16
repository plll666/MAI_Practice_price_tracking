"""merge_two_heads

Revision ID: c8535b0f3c07
Revises: 1cfb98fa0baf, alerts_table_initial
Create Date: 2026-04-16 12:59:53.766924

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8535b0f3c07'
down_revision: Union[str, Sequence[str], None] = ('1cfb98fa0baf', 'alerts_table_initial')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
