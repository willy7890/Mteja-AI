"""Realign training_data columns with the current TrainingData model.

Old shape (from earlier migrations): question, category, answer, verified
New shape (expected by app.models.training_data.TrainingData):
    intent, prompt, completion, status, user_id, created_at, updated_at

Revision ID: 20260930_realign_training_data
Revises: 20260929_email_verification
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260930_realign_training_data"
down_revision: Union[str, Sequence[str], None] = "20260929_email_verification"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _columns(bind):
    return {c["name"]: c for c in sa.inspect(bind).get_columns("training_data")}


def _indexes(bind):
    return {i["name"] for i in sa.inspect(bind).get_indexes("training_data")}


def upgrade() -> None:
    bind = op.get_bind()
    columns = _columns(bind)

    # 1. question -> prompt (VARCHAR(500) -> TEXT, a safe widening cast)
    if "question" in columns and "prompt" not in columns:
        op.alter_column("training_data", "question", new_column_name="prompt")
        columns = _columns(bind)
    if "prompt" in columns and not isinstance(columns["prompt"]["type"], sa.Text):
        op.alter_column("training_data", "prompt", type_=sa.Text(), existing_nullable=False)

    # 2. category -> intent, plus the index the model declares (index=True)
    if "category" in columns and "intent" not in columns:
        op.alter_column("training_data", "category", new_column_name="intent")
        columns = _columns(bind)
    if "intent" in columns and "ix_training_data_intent" not in _indexes(bind):
        op.create_index("ix_training_data_intent", "training_data", ["intent"], unique=False)

    # 3. answer -> completion
    if "answer" in columns and "completion" not in columns:
        op.alter_column("training_data", "answer", new_column_name="completion")
        columns = _columns(bind)

    # 4. verified (bool) -> status (string). Backfill from the old flag,
    #    then retire the flag.
    if "status" not in columns:
        op.add_column(
            "training_data",
            sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
        )
        columns = _columns(bind)
        if "verified" in columns:
            op.execute(
                "UPDATE training_data SET status = CASE WHEN verified THEN 'approved' ELSE 'pending' END"
            )
    if "verified" in columns:
        op.drop_column("training_data", "verified")

    # 5. user_id (nullable FK to users, SET NULL on delete)
    columns = _columns(bind)
    if "user_id" not in columns:
        op.add_column("training_data", sa.Column("user_id", sa.Integer(), nullable=True))
        op.create_foreign_key(
            "fk_training_data_user_id",
            "training_data",
            "users",
            ["user_id"],
            ["id"],
            ondelete="SET NULL",
        )

    # 6. updated_at (new bookkeeping column; ORM manages the value going
    #    forward via onupdate=, so the server_default is just for backfill)
    columns = _columns(bind)
    if "updated_at" not in columns:
        op.add_column(
            "training_data",
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.text("now()"),
            ),
        )
        op.alter_column("training_data", "updated_at", server_default=None)


def downgrade() -> None:
    bind = op.get_bind()
    columns = _columns(bind)

    if "updated_at" in columns:
        op.drop_column("training_data", "updated_at")

    columns = _columns(bind)
    if "user_id" in columns:
        op.drop_constraint("fk_training_data_user_id", "training_data", type_="foreignkey")
        op.drop_column("training_data", "user_id")

    columns = _columns(bind)
    if "verified" not in columns:
        op.add_column(
            "training_data",
            sa.Column("verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        )
        columns = _columns(bind)
        if "status" in columns:
            op.execute(
                "UPDATE training_data SET verified = (status = 'approved')"
            )
        op.alter_column("training_data", "verified", server_default=None)

    columns = _columns(bind)
    if "status" in columns:
        op.drop_column("training_data", "status")

    columns = _columns(bind)
    if "completion" in columns and "answer" not in columns:
        op.alter_column("training_data", "completion", new_column_name="answer")

    if "ix_training_data_intent" in _indexes(bind):
        op.drop_index("ix_training_data_intent", table_name="training_data")
    columns = _columns(bind)
    if "intent" in columns and "category" not in columns:
        op.alter_column("training_data", "intent", new_column_name="category")

    columns = _columns(bind)
    if "prompt" in columns and "question" not in columns:
        op.alter_column(
            "training_data", "prompt",
            type_=sa.String(length=500),
            new_column_name="question",
            existing_nullable=False,
        )