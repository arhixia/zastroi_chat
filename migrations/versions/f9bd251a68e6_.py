"""init

Revision ID: f9bd251a68e6
Revises:
Create Date: 2026-08-18 14:43:16.935856

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import pgvector.sqlalchemy

# revision identifiers, used by Alembic.
revision: str = 'f9bd251a68e6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('admins',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('username', sa.String(length=255), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('sites',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('domain', sa.String(length=255), nullable=False),
    sa.Column('allowed_origins', postgresql.ARRAY(sa.String()), nullable=False),
    sa.Column('crawl_start_urls', postgresql.ARRAY(sa.String()), server_default=sa.text("'{}'"), nullable=False),
    sa.Column('crawl_excluded_urls', postgresql.ARRAY(sa.String()), server_default=sa.text("'{}'"), nullable=False),
    sa.Column('widget_logo_url', sa.String(length=512), nullable=True),
    sa.Column('widget_primary_color', sa.String(length=16), nullable=False),
    sa.Column('widget_bot_name', sa.String(length=100), nullable=False),
    sa.Column('widget_welcome_message', sa.String(length=1000), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('domain')
    )
    op.create_table('chunks',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('site_id', sa.UUID(), nullable=False),
    sa.Column('source_type', sa.Enum('page', 'document', name='sourcetype'), nullable=False),
    sa.Column('source_id', sa.UUID(), nullable=False),
    sa.Column('source_label', sa.String(length=512), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('token_count', sa.Integer(), nullable=False),
    sa.Column('embedding', pgvector.sqlalchemy.vector.VECTOR(dim=1536), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['site_id'], ['sites.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('clients',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('site_id', sa.UUID(), nullable=False),
    sa.Column('phone', sa.String(length=20), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['site_id'], ['sites.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('site_id', 'phone', name='uq_client_site_phone')
    )
    op.create_table('crawl_runs',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('site_id', sa.UUID(), nullable=False),
    sa.Column('status', sa.Enum('running', 'success', 'failed', 'partial', name='crawlstatus'), nullable=False),
    sa.Column('pages_processed', sa.Integer(), nullable=False),
    sa.Column('pages_added', sa.Integer(), nullable=False),
    sa.Column('pages_updated', sa.Integer(), nullable=False),
    sa.Column('pages_stale', sa.Integer(), nullable=False),
    sa.Column('errors', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['site_id'], ['sites.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('documents',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('site_id', sa.UUID(), nullable=False),
    sa.Column('filename', sa.String(length=512), nullable=False),
    sa.Column('file_type', sa.Enum('pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx', name='documenttype'), nullable=False),
    sa.Column('storage_path', sa.String(length=1024), nullable=False),
    sa.Column('content_hash', sa.String(length=64), nullable=True),
    sa.Column('status', sa.Enum('active', 'excluded', name='documentstatus'), nullable=False),
    sa.Column('uploaded_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['site_id'], ['sites.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('pages',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('site_id', sa.UUID(), nullable=False),
    sa.Column('url', sa.String(length=2048), nullable=False),
    sa.Column('title', sa.String(length=512), nullable=True),
    sa.Column('content_hash', sa.String(length=64), nullable=True),
    sa.Column('status', sa.Enum('active', 'stale', 'excluded', name='pagestatus'), nullable=False),
    sa.Column('is_relevant', sa.Boolean(), nullable=False),
    sa.Column('last_crawled_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['site_id'], ['sites.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('conversations',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('site_id', sa.UUID(), nullable=False),
    sa.Column('client_id', sa.UUID(), nullable=True),
    sa.Column('session_id', sa.String(length=64), nullable=False),
    sa.Column('visitor_id', sa.String(length=64), nullable=False),
    sa.Column('first_page_url', sa.String(length=2048), nullable=True),
    sa.Column('current_page_url', sa.String(length=2048), nullable=True),
    sa.Column('referrer', sa.String(length=2048), nullable=True),
    sa.Column('utm', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('gclid', sa.String(length=255), nullable=True),
    sa.Column('yclid', sa.String(length=255), nullable=True),
    sa.Column('metrika_client_id', sa.String(length=64), nullable=True),
    sa.Column('device_type', sa.String(length=32), nullable=True),
    sa.Column('browser', sa.String(length=64), nullable=True),
    sa.Column('os', sa.String(length=64), nullable=True),
    sa.Column('ip_address', postgresql.INET(), nullable=True),
    sa.Column('detected_interest', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('messages_since_last_offer', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['site_id'], ['sites.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('leads',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('site_id', sa.UUID(), nullable=False),
    sa.Column('conversation_id', sa.UUID(), nullable=False),
    sa.Column('client_id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('phone', sa.String(length=20), nullable=False),
    sa.Column('consent_given_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('consent_text_version', sa.String(length=32), nullable=False),
    sa.Column('interest', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['site_id'], ['sites.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('messages',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('conversation_id', sa.UUID(), nullable=False),
    sa.Column('role', sa.Enum('user', 'assistant', 'system', name='messagerole'), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('sources', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('messages')
    op.drop_table('leads')
    op.drop_table('conversations')
    op.drop_table('pages')
    op.drop_table('documents')
    op.drop_table('crawl_runs')
    op.drop_table('clients')
    op.drop_table('chunks')
    op.drop_table('sites')
    op.drop_table('admins')