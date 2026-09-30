"""merge multiple heads

Revision ID: 05e8d100c99a
Revises: 20260915_handoff_fields, 37b292479b8f, cf84e33bce67
Create Date: 2026-09-16 11:03:51.658852
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "05e8d100c99a"

down_revision: Union[str, Sequence[str], None] = (
    "20260915_handoff_fields",
    "37b292479b8f",
    "cf84e33bce67",
)

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Merge multiple migration heads."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
