"""Added CASCADE on face_images and user_info

Revision ID: 9bb65c2ecbe2
Revises: dd80984dcf41
Create Date: 2024-11-11 17:18:39.610883

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9bb65c2ecbe2'
down_revision = 'dd80984dcf41'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('face_images', schema=None) as batch_op:
        batch_op.drop_constraint('face_images_ibfk_1', type_='foreignkey')
        batch_op.create_foreign_key(None, 'users', ['user_id'], ['id'], ondelete='CASCADE')

    with op.batch_alter_table('user_infos', schema=None) as batch_op:
        batch_op.drop_constraint('user_infos_ibfk_1', type_='foreignkey')
        batch_op.create_foreign_key(None, 'users', ['user_id'], ['id'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_infos', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('user_infos_ibfk_1', 'users', ['user_id'], ['id'])

    with op.batch_alter_table('face_images', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('face_images_ibfk_1', 'users', ['user_id'], ['id'])

    # ### end Alembic commands ###