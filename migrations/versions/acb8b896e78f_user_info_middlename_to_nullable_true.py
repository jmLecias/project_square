"""user_info middlename to nullable true

Revision ID: acb8b896e78f
Revises: b2af18319bcf
Create Date: 2024-12-02 01:57:37.600475

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'acb8b896e78f'
down_revision = 'b2af18319bcf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_infos', schema=None) as batch_op:
        batch_op.alter_column('middlename',
               existing_type=mysql.VARCHAR(length=255),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_infos', schema=None) as batch_op:
        batch_op.alter_column('middlename',
               existing_type=mysql.VARCHAR(length=255),
               nullable=False)

    # ### end Alembic commands ###
