"""Update garden_type table structure

Revision ID: 0700de7eaf6a
Revises: f6946342659e
Create Date: 2025-03-03 17:20:06.851128

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0700de7eaf6a'
down_revision = 'f6946342659e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('garden_type', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=15),
               type_=sa.String(length=50),
               existing_nullable=False)
        batch_op.drop_column('descripton')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('garden_type', schema=None) as batch_op:
        batch_op.add_column(sa.Column('descripton', sa.TEXT(), nullable=True))
        batch_op.alter_column('name',
               existing_type=sa.String(length=50),
               type_=sa.VARCHAR(length=15),
               existing_nullable=False)
        batch_op.drop_column('description')

    # ### end Alembic commands ###
