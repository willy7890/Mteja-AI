"""add_answer_to_training_data

Revision ID: 51c0e0e2c403
Revises: 20260915_handoff_fields
Create Date: 2026-09-14 06:25:03.143899

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "51c0e0e2c403"

down_revision: Union[str, Sequence[str], None] = "20260915_handoff_fields"

branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {c["name"] for c in inspector.get_columns("training_data")}
    indexes = {i["name"] for i in inspector.get_indexes("training_data")}

    if "answer" not in columns:
        op.add_column(
            "training_data",
            sa.Column("answer", sa.Text(), nullable=False),
        )

    # Idempotent in Postgres even if already this type/nullability, but we
    # only touch "question" if it hasn't already been narrowed to VARCHAR.
    if "question" in columns:
        op.alter_column(
            "training_data",
            "question",
            existing_type=sa.TEXT(),
            type_=sa.String(length=500),
            existing_nullable=False,
        )

    if "category" in columns:
        op.alter_column(
            "training_data",
            "category",
            existing_type=sa.VARCHAR(length=100),
            nullable=True,
        )

    if op.f("ix_training_data_id") not in indexes:
        op.create_index(
            op.f("ix_training_data_id"),
            "training_data",
            ["id"],
            unique=False,
        )

    if "verified" in columns:
        op.drop_column(
            "training_data",
            "verified",
        )

    if "created_at" in columns:
        op.drop_column(
            "training_data",
            "created_at",
        )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {c["name"] for c in inspector.get_columns("training_data")}
    indexes = {i["name"] for i in inspector.get_indexes("training_data")}

    if "created_at" not in columns:
        op.add_column(
            "training_data",
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
            ),
        )

    if "verified" not in columns:
        op.add_column(
            "training_data",
            sa.Column(
                "verified",
                sa.Boolean(),
                nullable=False,
            ),
        )

    if op.f("ix_training_data_id") in indexes:
        op.drop_index(
            op.f("ix_training_data_id"),
            table_name="training_data",
        )

    if "category" in columns:
        op.alter_column(
            "training_data",
            "category",
            existing_type=sa.VARCHAR(length=100),
            nullable=False,
        )

    if "question" in columns:
        op.alter_column(
            "training_data",
            "question",
            existing_type=sa.String(length=500),
            type_=sa.TEXT(),
            existing_nullable=False,
        )

    if "answer" in columns:
        op.drop_column(
            "training_data",
            "answer",
        )