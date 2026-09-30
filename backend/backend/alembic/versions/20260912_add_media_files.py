"""add media files table

Revision ID: 20260912_media_files
Revises: 89ed321bdb9d
"""

from alembic import op
import sqlalchemy as sa


revision = "20260912_media_files"
down_revision = "89ed321bdb9d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("media_files"):
        return

    op.create_table(
        "media_files",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("customer_id", sa.Integer(), nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=True),
        sa.Column("message_id", sa.Integer(), nullable=True),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("stored_filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("file_url", sa.String(length=500), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"]),
        sa.ForeignKeyConstraint(["message_id"], ["messages.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.UniqueConstraint("stored_filename"),
    )
    op.create_index("ix_media_files_id", "media_files", ["id"], unique=False)
    op.create_index("ix_media_files_customer_id", "media_files", ["customer_id"], unique=False)
    op.create_index("ix_media_files_conversation_id", "media_files", ["conversation_id"], unique=False)
    op.create_index("ix_media_files_message_id", "media_files", ["message_id"], unique=False)
    op.create_index("ix_media_files_organization_id", "media_files", ["organization_id"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    if not sa.inspect(bind).has_table("media_files"):
        return

    op.drop_index("ix_media_files_organization_id", table_name="media_files")
    op.drop_index("ix_media_files_message_id", table_name="media_files")
    op.drop_index("ix_media_files_conversation_id", table_name="media_files")
    op.drop_index("ix_media_files_customer_id", table_name="media_files")
    op.drop_index("ix_media_files_id", table_name="media_files")
    op.drop_table("media_files")
