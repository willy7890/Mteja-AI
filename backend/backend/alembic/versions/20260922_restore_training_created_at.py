"""Restore training_data.created_at expected by the ORM model."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260922_restore_created_at"
down_revision: Union[str, Sequence[str], None] = "e8c7f7765ec6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "training_data",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("training_data", "created_at")