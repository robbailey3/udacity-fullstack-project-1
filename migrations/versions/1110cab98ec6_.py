"""empty message

Revision ID: 1110cab98ec6
Revises: 902d51be56bf
Create Date: 2020-03-29 18:34:19.734502

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1110cab98ec6'
down_revision = '902d51be56bf'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Artist', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Artist', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    # ### end Alembic commands ###
