import sqlalchemy as sa
from sqlalchemy.schema import CreateTable

from .constants import GameState
from .async.db import *

metadata = sa.MetaData()

league_tbl = sa.Table('league', metadata,
    sa.Column('id', sa.SmallInteger, primary_key=True),
    sa.Column('name', sa.String(255))
)

team_tbl = sa.Table('team', metadata,
    sa.Column('id', sa.SmallInteger, primary_key=True),
    sa.Column('league', sa.SmallInteger, sa.ForeignKey('league.id'), nullable=False),
    sa.Column('name', sa.String),
    sa.Column('full_name', sa.String),
    sa.Column('city', sa.String)
)

game_tbl = sa.Table('game', metadata,
    sa.Column('id', sa.BigInteger, primary_key=True),
    sa.Column('season', sa.SmallInteger),
    sa.Column('status', sa.Enum(GameState)),
    sa.Column('away', sa.SmallInteger, sa.ForeignKey('team.id'), nullable=False),
    sa.Column('home', sa.SmallInteger, sa.ForeignKey('team.id'), nullable=False),
    sa.Column('away_score', sa.SmallInteger),
    sa.Column('home_score', sa.SmallInteger),
    sa.Column('start', sa.DateTime, index=True),
    sa.Column('duration', sa.Time),
    sa.Column('periods', sa.SmallInteger)
)