"""Added daily records and detection records

Revision ID: a582dc4135ab
Revises: 6eecd4688647
Create Date: 2024-11-14 04:21:37.668260

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a582dc4135ab'
down_revision = '6eecd4688647'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('daily_records',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('arrival', sa.Time(), nullable=True),
    sa.Column('departure', sa.Time(), nullable=True),
    sa.Column('undertime', mysql.BIGINT(), nullable=True),
    sa.Column('overtime', mysql.BIGINT(), nullable=True),
    sa.Column('am_time_in', sa.Time(), nullable=True),
    sa.Column('am_time_out', sa.Time(), nullable=True),
    sa.Column('pm_time_in', sa.Time(), nullable=True),
    sa.Column('pm_time_out', sa.Time(), nullable=True),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('detection_records',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('datetime', sa.DateTime(), nullable=False),
    sa.Column('type_id', sa.Integer(), nullable=False),
    sa.Column('location_id', sa.Integer(), nullable=False),
    sa.Column('image_origin_path', sa.String(length=255), nullable=False),
    sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['type_id'], ['camera_types.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('cameras', schema=None) as batch_op:
        batch_op.alter_column('type_id',
               existing_type=mysql.INTEGER(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cameras', schema=None) as batch_op:
        batch_op.alter_column('type_id',
               existing_type=mysql.INTEGER(),
               nullable=True)

    op.drop_table('detection_records')
    op.drop_table('daily_records')
    # ### end Alembic commands ###