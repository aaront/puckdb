"""First migration

Revision ID: 34cd4d697d99
Revises: 
Create Date: 2018-07-12 22:29:00.578168

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '34cd4d697d99'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('player',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('first_name', sa.String(), nullable=True),
                    sa.Column('last_name', sa.String(), nullable=True),
                    sa.Column('position', sa.Enum('center', 'left_wing', 'right_wing', 'defenseman', 'goalie',
                                                  name='player_position'), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('team',
                    sa.Column('id', sa.SmallInteger(), nullable=False),
                    sa.Column('name', sa.String(), nullable=True),
                    sa.Column('team_name', sa.String(), nullable=True),
                    sa.Column('abbreviation', sa.String(), nullable=True),
                    sa.Column('city', sa.String(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('game',
                    sa.Column('id', sa.BigInteger(), nullable=False),
                    sa.Column('version', sa.BigInteger(), nullable=False),
                    sa.Column('season', sa.Integer(), nullable=False),
                    sa.Column('type', sa.Enum('regular', 'playoff', 'allstar', name='game_type'), nullable=True),
                    sa.Column('away', sa.SmallInteger(), nullable=False),
                    sa.Column('home', sa.SmallInteger(), nullable=False),
                    sa.Column('date_start', sa.DateTime(timezone=True), nullable=True),
                    sa.Column('date_end', sa.DateTime(timezone=True), nullable=True),
                    sa.Column('first_star', sa.Integer(), nullable=True),
                    sa.Column('second_star', sa.Integer(), nullable=True),
                    sa.Column('third_star', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['away'], ['team.id'], ),
                    sa.ForeignKeyConstraint(['first_star'], ['player.id'], ),
                    sa.ForeignKeyConstraint(['home'], ['team.id'], ),
                    sa.ForeignKeyConstraint(['second_star'], ['player.id'], ),
                    sa.ForeignKeyConstraint(['third_star'], ['player.id'], ),
                    sa.PrimaryKeyConstraint('id', 'version')
                    )
    op.create_index(op.f('ix_game_date_start'), 'game', ['date_start'], unique=False)
    op.create_table('event',
                    sa.Column('game', sa.BigInteger(), nullable=False),
                    sa.Column('version', sa.BigInteger(), nullable=False),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('team', sa.SmallInteger(), nullable=False),
                    sa.Column('type',
                              sa.Enum('blocked_shot', 'challenge', 'faceoff', 'giveaway', 'goal', 'hit', 'missed_shot',
                                      'penalty', 'shot', 'stop', 'takeaway', name='event_type'), nullable=False),
                    sa.Column('date', sa.DateTime(timezone=True), nullable=False),
                    sa.Column('shot_type',
                              sa.Enum('backhand', 'deflected', 'slap', 'snap', 'tip', 'wrap_around', 'wrist',
                                      name='shot_type'), nullable=True),
                    sa.Column('period', sa.SmallInteger(), nullable=False),
                    sa.Column('location_x', sa.Float(), nullable=True),
                    sa.Column('location_y', sa.Float(), nullable=True),
                    sa.ForeignKeyConstraint(['game', 'version'], ['game.id', 'game.version'], ),
                    sa.ForeignKeyConstraint(['team'], ['team.id'], ),
                    sa.PrimaryKeyConstraint('game', 'version', 'id')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('event')
    op.drop_index(op.f('ix_game_date_start'), table_name='game')
    op.drop_table('game')
    op.drop_table('team')
    op.drop_table('player')
    # ### end Alembic commands ###
