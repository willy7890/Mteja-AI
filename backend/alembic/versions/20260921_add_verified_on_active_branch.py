"""Add the training-data verification flag on the active migration branch."""

from alembic import op


revision = "20260921_training_verified"
down_revision = "20260914_user_role"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE training_data
        ADD COLUMN IF NOT EXISTS verified BOOLEAN NOT NULL DEFAULT FALSE
        """
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE training_data DROP COLUMN IF EXISTS verified"
    )