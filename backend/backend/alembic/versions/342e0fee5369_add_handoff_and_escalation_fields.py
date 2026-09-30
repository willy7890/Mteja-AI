"""Align conversations table with current_handler / assigned_agent_id handoff model.

Revision ID: 20260915_handoff_fields
Revises: 20260914_user_role
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260915_handoff_fields"
down_revision: Union[str, Sequence[str], None] = "20260914_user_role"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {c["name"] for c in inspector.get_columns("conversations")}

    if "current_handler" not in columns:
        op.add_column(
            "conversations",
            sa.Column("current_handler", sa.String(30), nullable=False, server_default="ai"),
        )
        # data lives in `mode` today — carry it over before dropping
        if "mode" in columns:
            op.execute("UPDATE conversations SET current_handler = mode")
        op.alter_column("conversations", "current_handler", server_default=None)

    if "assigned_agent_id" not in columns:
        op.add_column(
            "conversations",
            sa.Column("assigned_agent_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        )
        if "assigned_to" in columns:
            op.execute("UPDATE conversations SET assigned_agent_id = assigned_to")

    if "escalation_reason" not in columns:
        op.add_column(
            "conversations",
            sa.Column("escalation_reason", sa.String(255), nullable=True),
        )

    if "escalated_at" not in columns:
        op.add_column(
            "conversations",
            sa.Column("escalated_at", sa.DateTime(timezone=True), nullable=True),
        )

    if "resolved_at" not in columns:
        op.add_column(
            "conversations",
            sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        )

    # drop the old columns now that data has been copied over
    if "mode" in columns:
        op.drop_column("conversations", "mode")
    if "assigned_to" in columns:
        op.drop_column("conversations", "assigned_to")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {c["name"] for c in inspector.get_columns("conversations")}

    if "mode" not in columns:
        op.add_column(
            "conversations",
            sa.Column("mode", sa.String(30), nullable=False, server_default="ai"),
        )
        if "current_handler" in columns:
            op.execute("UPDATE conversations SET mode = current_handler")
        op.alter_column("conversations", "mode", server_default=None)

    if "assigned_to" not in columns:
        op.add_column(
            "conversations",
            sa.Column("assigned_to", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        )
        if "assigned_agent_id" in columns:
            op.execute("UPDATE conversations SET assigned_to = assigned_agent_id")

    for col in ("escalation_reason", "escalated_at", "resolved_at", "current_handler", "assigned_agent_id"):
        if col in columns:
            op.drop_column("conversations", col)
