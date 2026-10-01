"""Restore training_data.created_at

Revision ID: 20260922_restore_created_at
Revises: e8c7f7765ec6
Create Date: 2026-09-22

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# Variables kuu za Alembic
revision: str = '20260922_restore_created_at'
down_revision: Union[str, None] = 'e8c7f7765ec6'  # Weka ID ya revision iliyotangulia kabla ya hii
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('training_data')]
    
    if 'created_at' not in columns:
        op.add_column(
            'training_data',
            sa.Column(
                'created_at',
                sa.TIMESTAMP(timezone=True),
                server_default=sa.text('now()'),
                nullable=False
            )
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('training_data')]
    
    if 'created_at' in columns:
        op.drop_column('training_data', 'created_at')