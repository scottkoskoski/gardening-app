"""Updated Plant model to include OpenFarm fields

Revision ID: e2c1f2be5cb5
Revises: b0264e719091
Create Date: 2025-02-13 17:00:38.920485

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e2c1f2be5cb5'
down_revision = 'b0264e719091'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('plant', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sowing_method', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('spread', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('row_spacing', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('height', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('image_url', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('plant', schema=None) as batch_op:
        batch_op.drop_column('image_url')
        batch_op.drop_column('description')
        batch_op.drop_column('height')
        batch_op.drop_column('row_spacing')
        batch_op.drop_column('spread')
        batch_op.drop_column('sowing_method')

    # ### end Alembic commands ###
