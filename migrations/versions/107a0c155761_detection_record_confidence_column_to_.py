"""Detection record confidence column to float

Revision ID: 107a0c155761
Revises: 799af551d509
Create Date: 2024-11-17 20:07:11.207741

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '107a0c155761'
down_revision = '799af551d509'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('detection_records', schema=None) as batch_op:
        batch_op.alter_column('confidence',
               existing_type=mysql.INTEGER(),
               type_=sa.Float(),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('detection_records', schema=None) as batch_op:
        batch_op.alter_column('confidence',
               existing_type=sa.Float(),
               type_=mysql.INTEGER(),
               existing_nullable=False)

    # ### end Alembic commands ###