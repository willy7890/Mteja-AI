"""Add trial dates and admin verification state to users."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260924_trial_verification"
down_revision: Union[str, Sequence[str], None] = "20260923_repair_created_at"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("users")}
    if "is_verified" not in columns:
        op.add_column("users", sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.true()))
        op.alter_column("users", "is_verified", server_default=None)
    if "avatar_url" not in columns:
        op.add_column("users", sa.Column("avatar_url", sa.String(length=500), nullable=True))
    if "trial_started_at" not in columns:
        op.add_column("users", sa.Column("trial_started_at", sa.DateTime(timezone=True), nullable=True))
    if "trial_ends_at" not in columns:
        op.add_column("users", sa.Column("trial_ends_at", sa.DateTime(timezone=True), nullable=True))

    op.execute(
        "UPDATE users SET is_superuser = TRUE, is_verified = TRUE "
        "WHERE lower(email) = 'wilbardmagaso777@gmail.com'"
    )
    op.execute(
        "UPDATE users SET is_verified = FALSE, role = 'ADMIN' "
        "WHERE lower(email) = 'admin@mteja-ai.co.tz'"
    )


def downgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("users")}
    for column in ("trial_ends_at", "trial_started_at", "is_verified"):
        if column in columns:
            op.drop_column("users", column)