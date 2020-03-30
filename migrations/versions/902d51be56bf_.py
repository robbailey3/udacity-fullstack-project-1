"""empty message

Revision ID: 902d51be56bf
Revises: 3030edcdc7a9
Create Date: 2020-03-29 15:57:26.741780

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '902d51be56bf'
down_revision = '3030edcdc7a9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('artist_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'Show', 'Artist', ['artist_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Show', type_='foreignkey')
    op.drop_column('Show', 'artist_id')
    # ### end Alembic commands ###
