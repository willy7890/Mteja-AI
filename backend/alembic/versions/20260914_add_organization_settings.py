"""Add organization and AI settings JSON fields.

Revision ID: 20260914_org_settings
Revises: 277eafd99612
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260914_org_settings"
down_revision: Union[str, Sequence[str], None] = "277eafd99612"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("organizations")}
    if "settings" not in columns:
        op.add_column("organizations", sa.Column("settings", sa.JSON(), nullable=False, server_default="{}"))
    if "ai_settings" not in columns:
        op.add_column("organizations", sa.Column("ai_settings", sa.JSON(), nullable=False, server_default="{}"))
    op.alter_column("organizations", "settings", server_default=None)
    op.alter_column("organizations", "ai_settings", server_default=None)


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("organizations")}
    if "ai_settings" in columns:
        op.drop_column("organizations", "ai_settings")
    if "settings" in columns:
        op.drop_column("organizations", "settings")
