"""Add profile_pic and show_email to User

Revision ID: 2ddf354a5a29
Revises: <previous_revision_id>
Create Date: 2025-05-15 19:06:52.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2ddf354a5a29'
down_revision = '38f6771a6ec5'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('user', sa.Column('profile_pic', sa.String(length=256), nullable=True, server_default='default.png'))
    op.add_column('user', sa.Column('show_email', sa.Boolean(), nullable=True, server_default='0'))

def downgrade():
    op.drop_column('user', 'profile_pic')
    op.drop_column('user', 'show_email')