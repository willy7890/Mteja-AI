"""verify_sync

Revision ID: 37b292479b8f
Revises: 51c0e0e2c403
Create Date: 2026-09-14 06:53:30.768873

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "37b292479b8f"

down_revision: Union[str, Sequence[str], None] = "51c0e0e2c403"

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
