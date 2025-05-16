"""Add show_stats and show_bets columns to User

Revision ID: 0f7bb5e554f3
Revises: 62fb0afc1fdd
Create Date: 2025-05-16 10:06:00.360162

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0f7bb5e554f3'
down_revision = '62fb0afc1fdd'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('show_stats', sa.Boolean(), server_default='0', nullable=True))
    op.add_column('user', sa.Column('show_bets', sa.Boolean(), server_default='0', nullable=True))


def downgrade():
    op.drop_column('user', 'show_bets')
    op.drop_column('user', 'show_stats')