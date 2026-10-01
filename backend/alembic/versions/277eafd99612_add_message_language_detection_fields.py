"""add message language detection fields

Revision ID: 277eafd99612
Revises: 20260913_whatsapp_window
Create Date: 2026-09-13 20:43:16.346155

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '277eafd99612'
down_revision: Union[str, Sequence[str], None] = '20260913_whatsapp_window'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # NOTE: these five CREATE TABLEs were auto-generated alongside the
    # language-detection columns below, but some of them were *also*
    # created by an earlier migration in this history (89ed321bdb9d,
    # "safe schema synchronization"). Guard each one with has_table() so
    # this migration is safe to run regardless of which branch created
    # them first.
    if not inspector.has_table('agent_configurations'):
        op.create_table('agent_configurations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('agent_name', sa.String(), nullable=True),
        sa.Column('system_prompt', sa.Text(), nullable=True),
        sa.Column('model_name', sa.String(), nullable=True),
        sa.Column('temperature', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id')
        )
        op.create_index(op.f('ix_agent_configurations_id'), 'agent_configurations', ['id'], unique=False)

    if not inspector.has_table('campaigns'):
        op.create_table('campaigns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('channel', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_campaigns_id'), 'campaigns', ['id'], unique=False)

    if not inspector.has_table('channel_integrations'):
        op.create_table('channel_integrations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('channel_name', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('credentials_json', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_channel_integrations_id'), 'channel_integrations', ['id'], unique=False)

    if not inspector.has_table('integrations'):
        op.create_table('integrations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('service_name', sa.String(), nullable=False),
        sa.Column('is_connected', sa.Boolean(), nullable=True),
        sa.Column('config_data', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_integrations_id'), 'integrations', ['id'], unique=False)

    if not inspector.has_table('leads'):
        op.create_table('leads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_leads_id'), 'leads', ['id'], unique=False)

    # --- this is the part this migration is actually named for ---
    if inspector.has_table('media_files'):
        media_columns = {c["name"] for c in inspector.get_columns('media_files')}
        if 'created_at' in media_columns:
            op.alter_column('media_files', 'created_at',
                       existing_type=postgresql.TIMESTAMP(timezone=True),
                       nullable=False,
                       existing_server_default=sa.text('now()'))

    message_columns = {c["name"] for c in inspector.get_columns('messages')}
    if 'detected_language' not in message_columns:
        op.add_column('messages', sa.Column('detected_language', sa.String(length=50), nullable=True))
    if 'language_confidence' not in message_columns:
        op.add_column('messages', sa.Column('language_confidence', sa.Float(), nullable=True))
    if 'is_sheng' not in message_columns:
        op.add_column('messages', sa.Column('is_sheng', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    if 'is_code_switching' not in message_columns:
        op.add_column('messages', sa.Column('is_code_switching', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    message_columns = {c["name"] for c in inspector.get_columns('messages')}
    for col in ('is_code_switching', 'is_sheng', 'language_confidence', 'detected_language'):
        if col in message_columns:
            op.drop_column('messages', col)

    if inspector.has_table('media_files'):
        media_columns = {c["name"] for c in inspector.get_columns('media_files')}
        if 'created_at' in media_columns:
            op.alter_column('media_files', 'created_at',
                       existing_type=postgresql.TIMESTAMP(timezone=True),
                       nullable=True,
                       existing_server_default=sa.text('now()'))

    for table, index in (
        ('leads', 'ix_leads_id'),
        ('integrations', 'ix_integrations_id'),
        ('channel_integrations', 'ix_channel_integrations_id'),
        ('campaigns', 'ix_campaigns_id'),
        ('agent_configurations', 'ix_agent_configurations_id'),
    ):
        if inspector.has_table(table):
            op.drop_index(op.f(index), table_name=table)
            op.drop_table(table)