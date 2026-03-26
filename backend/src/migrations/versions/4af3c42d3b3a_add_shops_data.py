"""add_shops_data

Revision ID: 4af3c42d3b3a
Revises: cdd971c71193
Create Date: 2026-03-26 16:49:24.794640

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4af3c42d3b3a'
down_revision: Union[str, Sequence[str], None] = 'cdd971c71193'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    shops_table = sa.table(
        'shops',
        sa.column('id', sa.Integer),
        sa.column('name', sa.String),
        sa.column('domain', sa.String),
        sa.column('is_active', sa.Boolean)
    )

    op.bulk_insert(shops_table, [
        {'id': 1, 'name': 'Citilink', 'domain': 'citilink.ru', 'is_active': True},
    ])
    
    op.execute("SELECT setval('shops_id_seq', (SELECT max(id) FROM shops))")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM shops WHERE id IN (1)")
