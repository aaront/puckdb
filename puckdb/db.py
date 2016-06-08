import sqlalchemy as sa

from .constants import GameState, GameEvent
from .conf import get_db

metadata = sa.MetaData()

league_tbl = sa.Table('league', metadata,
    sa.Column('id', sa.SmallInteger, primary_key=True),
    sa.Column('name', sa.String(255))
)

team_tbl = sa.Table('team', metadata,
    sa.Column('id', sa.SmallInteger, primary_key=True),
    sa.Column('league', sa.SmallInteger, sa.ForeignKey('league.id'), nullable=False),
    sa.Column('name', sa.String),
    sa.Column('short_name', sa.String),
    sa.Column('abbreviation', sa.String),
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

event_tbl = sa.Table('event', metadata,
    sa.Column('game_id', sa.BigInteger, sa.ForeignKey('game.id'), nullable=False),
    sa.Column('type', sa.Enum(GameEvent), nullable=False)
)


def create():
    engine = sa.create_engine(get_db())
    metadata.drop_all(engine)
    metadata.create_all(engine)
    engine.execute(league_tbl.insert().values(
        id=0,
        name='NHL'
    ))
