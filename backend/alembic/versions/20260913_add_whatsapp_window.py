"""Add WhatsApp conversation window state.

Revision ID: 20260913_whatsapp_window
Revises: 20260913_schema_merge
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260913_whatsapp_window"
down_revision: Union[str, Sequence[str], None] = "20260913_schema_merge"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("conversations")}
    if "whatsapp_window_open" not in columns:
        op.add_column(
            "conversations",
            sa.Column(
                "whatsapp_window_open",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
        )
        op.alter_column("conversations", "whatsapp_window_open", server_default=None)


def downgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("conversations")}
    if "whatsapp_window_open" in columns:
        op.drop_column("conversations", "whatsapp_window_open")