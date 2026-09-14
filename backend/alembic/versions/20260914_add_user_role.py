"""Add role-based authorization to users.

Revision ID: 20260914_user_role
Revises: 20260914_org_settings
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "20260914_user_role"
down_revision: Union[str, Sequence[str], None] = "20260914_org_settings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "role" in columns:
        return

    if bind.dialect.name == "postgresql":
        role_enum = postgresql.ENUM("OWNER", "ADMIN", "AGENT", name="userrole")
        role_enum.create(bind, checkfirst=True)
        op.add_column(
            "users",
            sa.Column(
                "role",
                role_enum,
                nullable=False,
                server_default="AGENT",
            ),
        )
    else:
        op.add_column(
            "users",
            sa.Column("role", sa.String(length=20), nullable=False, server_default="agent"),
        )
    op.alter_column("users", "role", server_default=None)


def downgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("users")}
    if "role" in columns:
        op.drop_column("users", "role")
    if bind.dialect.name == "postgresql":
        postgresql.ENUM("OWNER", "ADMIN", "AGENT", name="userrole").drop(bind, checkfirst=True)
