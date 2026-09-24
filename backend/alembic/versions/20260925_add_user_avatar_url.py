"""Add persistent profile avatar URL to users."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260925_user_avatar_url"
down_revision: Union[str, Sequence[str], None] = "20260924_trial_verification"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("users")}
    if "avatar_url" not in columns:
        op.add_column("users", sa.Column("avatar_url", sa.String(length=500), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    columns = {column["name"] for column in sa.inspect(bind).get_columns("users")}
    if "avatar_url" in columns:
        op.drop_column("users", "avatar_url")