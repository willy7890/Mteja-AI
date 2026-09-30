"""merge final migration heads

Revision ID: e8c7f7765ec6
Revises: 20260921_training_verified, 7305268d1ae0
Create Date: 2026-09-22 14:22:27.435715

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8c7f7765ec6'
down_revision: Union[str, Sequence[str], None] = ('20260921_training_verified', '7305268d1ae0')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
