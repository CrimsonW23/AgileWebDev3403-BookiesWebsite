"""empty message

Revision ID: d67dafba076d
Revises: 
Create Date: 2025-05-02 14:47:44.688572

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd67dafba076d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=50), nullable=True),
    sa.Column('body', sa.String(length=150), nullable=True),
    sa.Column('category', sa.String(length=25), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('author', sa.String(length=25), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_post_author'), ['author'], unique=False)
        batch_op.create_index(batch_op.f('ix_post_body'), ['body'], unique=False)
        batch_op.create_index(batch_op.f('ix_post_category'), ['category'], unique=False)
        batch_op.create_index(batch_op.f('ix_post_timestamp'), ['timestamp'], unique=False)
        batch_op.create_index(batch_op.f('ix_post_title'), ['title'], unique=False)

    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=25), nullable=True),
    sa.Column('password', sa.String(length=150), nullable=True),
    sa.Column('email', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_user_password'), ['password'], unique=False)
        batch_op.create_index(batch_op.f('ix_user_username'), ['username'], unique=True)

    op.create_table('reply',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.String(length=150), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('author', sa.String(length=25), nullable=True),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('reply', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_reply_author'), ['author'], unique=False)
        batch_op.create_index(batch_op.f('ix_reply_body'), ['body'], unique=False)
        batch_op.create_index(batch_op.f('ix_reply_timestamp'), ['timestamp'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('reply', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_reply_timestamp'))
        batch_op.drop_index(batch_op.f('ix_reply_body'))
        batch_op.drop_index(batch_op.f('ix_reply_author'))

    op.drop_table('reply')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_username'))
        batch_op.drop_index(batch_op.f('ix_user_password'))
        batch_op.drop_index(batch_op.f('ix_user_email'))

    op.drop_table('user')
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_post_title'))
        batch_op.drop_index(batch_op.f('ix_post_timestamp'))
        batch_op.drop_index(batch_op.f('ix_post_category'))
        batch_op.drop_index(batch_op.f('ix_post_body'))
        batch_op.drop_index(batch_op.f('ix_post_author'))

    op.drop_table('post')
    # ### end Alembic commands ###