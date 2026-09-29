"""Add email verification and password reset OTP purposes."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260929_email_verification"
down_revision: Union[str, Sequence[str], None] = "20260925_user_avatar_url"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            "ALTER TYPE otppurpose ADD VALUE IF NOT EXISTS 'EMAIL_VERIFICATION'"
        )
        op.execute("ALTER TYPE otppurpose ADD VALUE IF NOT EXISTS 'PASSWORD_RESET'")

    columns = {column["name"] for column in sa.inspect(bind).get_columns("users")}
    if "email_verified" not in columns:
        op.add_column(
            "users",
            sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.true()),
        )
        op.execute("UPDATE users SET email_verified = TRUE")
        if bind.dialect.name == "postgresql":
            op.alter_column("users", "email_verified", server_default=sa.false())


def downgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("users")}
    if "email_verified" in columns:
        op.drop_column("users", "email_verified")