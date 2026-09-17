"""add verified column to training_data

Revision ID: dc0dccb6c3f7
Revises: 05e8d100c99a
Create Date: 2026-09-16 11:04:09.085165

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc0dccb6c3f7'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('training_data', sa.Column('verified', sa.Boolean(), server_default='false', nullable=False))
    


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('training_data', 'verified')
