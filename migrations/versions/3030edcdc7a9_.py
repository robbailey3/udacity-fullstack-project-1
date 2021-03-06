"""empty message

Revision ID: 3030edcdc7a9
Revises: ea1b9be02caf
Create Date: 2020-03-29 15:53:55.624177

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3030edcdc7a9'
down_revision = 'ea1b9be02caf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('seeking_description', sa.String(length=255), nullable=True))
    op.add_column('Artist', sa.Column('seeking_venue', sa.Boolean(), nullable=True))
    op.add_column('Artist', sa.Column('website', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Artist', 'website')
    op.drop_column('Artist', 'seeking_venue')
    op.drop_column('Artist', 'seeking_description')
    # ### end Alembic commands ###
