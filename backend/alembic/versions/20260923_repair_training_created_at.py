"""Repair training_data.created_at when the restore revision was skipped."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260923_repair_created_at"
down_revision: Union[str, Sequence[str], None] = "20260922_restore_created_at"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("training_data"):
        return

    columns = {column["name"] for column in inspector.get_columns("training_data")}
    if "created_at" not in columns:
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
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("training_data"):
        columns = {column["name"] for column in inspector.get_columns("training_data")}
        if "created_at" in columns:
            op.drop_column("training_data", "created_at")