"""Added more columns to Player

Revision ID: 5d216df3df20
Revises: 34cd4d697d99
Create Date: 2018-08-15 13:50:02.480018

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '5d216df3df20'
down_revision = '34cd4d697d99'
branch_labels = None
depends_on = None


def upgrade():
    player_handedness = postgresql.ENUM('left', 'right', name='player_handedness')
    player_handedness.create(op.get_bind())

    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('player', sa.Column('alternate_captain', sa.Boolean(), nullable=True))
    op.add_column('player', sa.Column('birth_city', sa.String(), nullable=True))
    op.add_column('player', sa.Column('birth_country', sa.String(), nullable=True))
    op.add_column('player', sa.Column('birth_date', sa.Date(), nullable=True))
    op.add_column('player', sa.Column('birth_state_province', sa.String(), nullable=True))
    op.add_column('player', sa.Column('captain', sa.Boolean(), nullable=True))
    op.add_column('player', sa.Column('handedness', sa.Enum('left', 'right', name='player_handedness'), nullable=True))
    op.add_column('player', sa.Column('height', sa.String(), nullable=True))
    op.add_column('player', sa.Column('nationality', sa.String(), nullable=True))
    op.add_column('player', sa.Column('weight', sa.SmallInteger(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('player', 'weight')
    op.drop_column('player', 'nationality')
    op.drop_column('player', 'height')
    op.drop_column('player', 'handedness')
    op.drop_column('player', 'captain')
    op.drop_column('player', 'birth_state_province')
    op.drop_column('player', 'birth_date')
    op.drop_column('player', 'birth_country')
    op.drop_column('player', 'birth_city')
    op.drop_column('player', 'alternate_captain')
    # ### end Alembic commands ###

    op.execute('DROP TYPE player_handedness;')