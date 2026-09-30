"""Add conversation timestamps and complete training data schema.

Revision ID: 20260913_schema_merge
Revises: 20260912_media_files, cf84e33bce67
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260913_schema_merge"
down_revision: Union[str, Sequence[str], None] = (
    "20260912_media_files",
    "cf84e33bce67",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    conversation_columns = {
        column["name"] for column in inspector.get_columns("conversations")
    }
    if "last_customer_message_at" not in conversation_columns:
        op.add_column(
            "conversations",
            sa.Column("last_customer_message_at", sa.DateTime(timezone=True), nullable=True),
        )

    if inspector.has_table("training_data"):
        training_columns = {
            column["name"] for column in inspector.get_columns("training_data")
        }
        if "answer" not in training_columns:
            op.add_column(
                "training_data",
                sa.Column("answer", sa.Text(), nullable=False, server_default=""),
            )
            op.alter_column("training_data", "answer", server_default=None)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("training_data"):
        training_columns = {
            column["name"] for column in inspector.get_columns("training_data")
        }
        if "answer" in training_columns:
            op.drop_column("training_data", "answer")

    conversation_columns = {
        column["name"] for column in inspector.get_columns("conversations")
    }
    if "last_customer_message_at" in conversation_columns:
        op.drop_column("conversations", "last_customer_message_at")