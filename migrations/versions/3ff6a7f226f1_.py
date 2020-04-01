"""empty message

Revision ID: 3ff6a7f226f1
Revises: 23833d608093
Create Date: 2020-03-31 21:24:49.102372

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3ff6a7f226f1'
down_revision = '23833d608093'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('Show_venue_id_fkey', 'Show', type_='foreignkey')
    op.create_foreign_key(None, 'Show', 'Venue', ['venue_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Show', type_='foreignkey')
    op.create_foreign_key('Show_venue_id_fkey', 'Show', 'Venue', ['venue_id'], ['id'])
    # ### end Alembic commands ###