import asyncio
import os
import contextlib

import sqlalchemy as sa
from aiopg import sa as async_sa

from .constants import GameState, GameEvent

metadata = sa.MetaData()

connect_str = os.getenv('PUCKDB_DATABASE', None)

team_tbl = sa.Table('team', metadata,
    sa.Column('id', sa.SmallInteger, primary_key=True),
    sa.Column('name', sa.String),
    sa.Column('short_name', sa.String),
    sa.Column('abbreviation', sa.String),
    sa.Column('city', sa.String)
)

game_tbl = sa.Table('game', metadata,
    sa.Column('id', sa.BigInteger, primary_key=True),
    sa.Column('season', sa.SmallInteger),
    sa.Column('status', sa.Enum(GameState, name='game_state')),
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
    sa.Column('type', sa.Enum(GameEvent, name='game_event'), nullable=False)
)


@contextlib.contextmanager
async def create_connection(loop: asyncio.AbstractEventLoop, dsn: str = None):
    async with async_sa.create_engine(dsn=dsn or connect_str, loop=loop) as engine:
        async with engine.acquire() as conn:
            await conn


def create(dsn=None):
    engine = sa.create_engine(dsn or connect_str)
    metadata.drop_all(engine)
    metadata.create_all(engine)


def drop(dsn=None):
    engine = sa.create_engine(dsn or connect_str)
    metadata.drop_all(engine)
