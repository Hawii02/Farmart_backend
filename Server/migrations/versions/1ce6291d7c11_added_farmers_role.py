"""added farmers role

Revision ID: 1ce6291d7c11
Revises: 2a97487077c4
Create Date: 2024-05-25 21:08:54.843611

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1ce6291d7c11'
down_revision = '2a97487077c4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('farmers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('address', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('role', sa.String(length=10), nullable=False))
        batch_op.drop_column('location')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('farmers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('location', sa.VARCHAR(length=100), nullable=True))
        batch_op.drop_column('role')
        batch_op.drop_column('address')

    # ### end Alembic commands ###