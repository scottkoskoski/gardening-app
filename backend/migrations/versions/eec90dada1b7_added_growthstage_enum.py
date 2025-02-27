"""Added GrowthStage Enum

Revision ID: eec90dada1b7
Revises: da915219fd44
Create Date: 2025-02-19 18:58:28.778655

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eec90dada1b7'
down_revision = 'da915219fd44'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_garden_plant', schema=None) as batch_op:
        batch_op.alter_column('growth_stage',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.Enum('SEEDLING', 'VEGETATIVE', 'FLOWERING', 'FRUITING', name='growthstage'),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_garden_plant', schema=None) as batch_op:
        batch_op.alter_column('growth_stage',
               existing_type=sa.Enum('SEEDLING', 'VEGETATIVE', 'FLOWERING', 'FRUITING', name='growthstage'),
               type_=sa.VARCHAR(length=50),
               nullable=True)

    # ### end Alembic commands ###
