"""safe schema synchronization

Revision ID: 89ed321bdb9d
Revises:
Create Date: 2026-09-09
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.core.database import Base
from app.models import (
    activity_log,
    agent,
    campaign,
    channel,
    conversation,
    customer,
    deal,
    integration,
    lead,
    message,
    media,
    organization,
    otp,
    stock,
    telegram,
    user,
)


# revision identifiers, used by Alembic.
revision: str = "89ed321bdb9d"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(inspector, table_name: str, column_name: str) -> bool:
    columns = inspector.get_columns(table_name)
    return any(column["name"] == column_name for column in columns)


def _has_table(inspector, table_name: str) -> bool:
    return inspector.has_table(table_name)


def _has_index(inspector, table_name: str, index_name: str) -> bool:
    indexes = inspector.get_indexes(table_name)
    return any(index["name"] == index_name for index in indexes)


def upgrade() -> None:
    """Safely synchronize the existing database schema."""

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # This project had no initial Alembic revision, so a fresh database has
    # no tables for the conditional changes below to inspect.
    if not _has_table(inspector, "users"):
        Base.metadata.create_all(bind)
        inspector = sa.inspect(bind)

    # ---------------------------------------------------------
    # USERS
    # ---------------------------------------------------------
    if not _has_column(inspector, "users", "is_superuser"):
        op.add_column(
            "users",
            sa.Column(
                "is_superuser",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
        )

        op.alter_column(
            "users",
            "is_superuser",
            server_default=None,
        )

    # ---------------------------------------------------------
    # CONVERSATIONS
    # ---------------------------------------------------------
    if not _has_column(
        inspector,
        "conversations",
        "external_participant_id",
    ):
        op.add_column(
            "conversations",
            sa.Column(
                "external_participant_id",
                sa.String(length=255),
                nullable=True,
            ),
        )

    # Refresh inspector after adding column.
    inspector = sa.inspect(bind)

    if not _has_index(
        inspector,
        "conversations",
        "ix_conversations_external_participant_id",
    ):
        op.create_index(
            "ix_conversations_external_participant_id",
            "conversations",
            ["external_participant_id"],
            unique=False,
        )

    if not _has_column(inspector, "conversations", "metadata"):
        op.add_column(
            "conversations",
            sa.Column(
                "metadata",
                sa.JSON(),
                nullable=True,
            ),
        )

    if not _has_column(inspector, "conversations", "updated_at"):
        op.add_column(
            "conversations",
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
        )

    # ---------------------------------------------------------
    # MESSAGES
    # ---------------------------------------------------------
    inspector = sa.inspect(bind)

    if not _has_column(inspector, "messages", "direction"):
        op.add_column(
            "messages",
            sa.Column(
                "direction",
                sa.String(length=10),
                nullable=False,
                server_default="inbound",
            ),
        )

        op.alter_column(
            "messages",
            "direction",
            server_default=None,
        )

    inspector = sa.inspect(bind)

    if not _has_column(inspector, "messages", "channel"):
        op.add_column(
            "messages",
            sa.Column(
                "channel",
                sa.String(length=50),
                nullable=False,
                server_default="web",
            ),
        )

        op.alter_column(
            "messages",
            "channel",
            server_default=None,
        )

    inspector = sa.inspect(bind)

    if not _has_column(inspector, "messages", "status"):
        op.add_column(
            "messages",
            sa.Column(
                "status",
                sa.String(length=20),
                nullable=False,
                server_default="sent",
            ),
        )

        op.alter_column(
            "messages",
            "status",
            server_default=None,
        )

    inspector = sa.inspect(bind)

    if not _has_column(inspector, "messages", "external_id"):
        op.add_column(
            "messages",
            sa.Column(
                "external_id",
                sa.String(length=255),
                nullable=True,
            ),
        )

    inspector = sa.inspect(bind)

    if not _has_index(
        inspector,
        "messages",
        "ix_messages_external_id",
    ):
        op.create_index(
            "ix_messages_external_id",
            "messages",
            ["external_id"],
            unique=False,
        )

    inspector = sa.inspect(bind)

    if not _has_column(
        inspector,
        "messages",
        "channel_metadata",
    ):
        op.add_column(
            "messages",
            sa.Column(
                "channel_metadata",
                sa.JSON(),
                nullable=True,
            ),
        )

    if not _has_column(inspector, "messages", "sent_at"):
        op.add_column(
            "messages",
            sa.Column(
                "sent_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
        )

    if not _has_column(inspector, "messages", "delivered_at"):
        op.add_column(
            "messages",
            sa.Column(
                "delivered_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
        )

    if not _has_column(inspector, "messages", "read_at"):
        op.add_column(
            "messages",
            sa.Column(
                "read_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
        )


def downgrade() -> None:
    """Reverse the schema synchronization."""

    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # Messages
    if _has_column(inspector, "messages", "read_at"):
        op.drop_column("messages", "read_at")

    inspector = sa.inspect(bind)

    if _has_column(inspector, "messages", "delivered_at"):
        op.drop_column("messages", "delivered_at")

    inspector = sa.inspect(bind)

    if _has_column(inspector, "messages", "sent_at"):
        op.drop_column("messages", "sent_at")

    inspector = sa.inspect(bind)

    if _has_column(inspector, "messages", "channel_metadata"):
        op.drop_column("messages", "channel_metadata")

    inspector = sa.inspect(bind)

    if _has_column(inspector, "messages", "external_id"):
        if _has_index(
            inspector,
            "messages",
            "ix_messages_external_id",
        ):
            op.drop_index(
                "ix_messages_external_id",
                table_name="messages",
            )

        op.drop_column("messages", "external_id")

    inspector = sa.inspect(bind)

    if _has_column(inspector, "messages", "status"):
        op.drop_column("messages", "status")

    inspector = sa.inspect(bind)

    if _has_column(inspector, "messages", "channel"):
        op.drop_column("messages", "channel")

    inspector = sa.inspect(bind)

    if _has_column(inspector, "messages", "direction"):
        op.drop_column("messages", "direction")

    # Conversations
    inspector = sa.inspect(bind)

    if _has_column(inspector, "conversations", "updated_at"):
        op.drop_column("conversations", "updated_at")

    inspector = sa.inspect(bind)

    if _has_column(inspector, "conversations", "metadata"):
        op.drop_column("conversations", "metadata")

    inspector = sa.inspect(bind)

    if _has_column(
        inspector,
        "conversations",
        "external_participant_id",
    ):
        if _has_index(
            inspector,
            "conversations",
            "ix_conversations_external_participant_id",
        ):
            op.drop_index(
                "ix_conversations_external_participant_id",
                table_name="conversations",
            )

        op.drop_column(
            "conversations",
            "external_participant_id",
        )

    # Users
    inspector = sa.inspect(bind)

    if _has_column(inspector, "users", "is_superuser"):
        op.drop_column("users", "is_superuser")
