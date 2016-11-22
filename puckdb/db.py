import asyncio
import os
from typing import List

import sqlalchemy as sa
from sqlalchemy.sql.dml import Insert
from aiopg import sa as async_sa

from puckdb.models import GameState, EventType, ShotAim, ShotType

metadata = sa.MetaData()

connect_str = os.getenv('PUCKDB_DATABASE', None)

team_tbl = sa.Table('team', metadata,
    sa.Column('id', sa.SmallInteger, primary_key=True),
    sa.Column('name', sa.String),
    sa.Column('team_name', sa.String),
    sa.Column('abbreviation', sa.String),
    sa.Column('city', sa.String)
)

game_tbl = sa.Table('game', metadata,
    sa.Column('id', sa.BigInteger, primary_key=True),
    sa.Column('season', sa.SmallInteger),
    sa.Column('status', sa.Enum(GameState, name='game_state')),
    sa.Column('away', sa.SmallInteger, sa.ForeignKey('team.id'), nullable=False),
    sa.Column('home', sa.SmallInteger, sa.ForeignKey('team.id'), nullable=False),
    sa.Column('start', sa.DateTime, index=True),
    sa.Column('end', sa.DateTime),
    sa.Column('periods', sa.SmallInteger)
)

event_tbl = sa.Table('event', metadata,
    sa.Column('game', sa.BigInteger, sa.ForeignKey('game.id'), nullable=False, primary_key=True),
    sa.Column('id', sa.Integer, nullable=False, primary_key=True),
    sa.Column('team', sa.SmallInteger, sa.ForeignKey('team.id'), nullable=False),
    sa.Column('type', sa.Enum(EventType, name='game_event'), nullable=False),
    sa.Column('time', sa.Time, nullable=False),
    sa.Column('shot_type', sa.Enum(ShotType, name='shot_type'), nullable=False),
    sa.Column('shot_aim', sa.Enum(ShotAim, name='shot_aim'), nullable=False),
    sa.Column('strength', sa.String),
    sa.Column('period', sa.SmallInteger, nullable=False)
)

async def execute(command_or_commands: Insert or List[Insert], loop: asyncio.AbstractEventLoop, dsn: str = None):
    async with async_sa.create_engine(dsn=dsn or connect_str, loop=loop) as engine:
        async with engine.acquire() as conn:
            if isinstance(command_or_commands, Insert):
                command_or_commands = [command_or_commands]
            for command in command_or_commands:
                await conn.execute(command)


def create(dsn=None):
    engine = sa.create_engine(dsn or connect_str)
    metadata.drop_all(engine)
    metadata.create_all(engine)


def drop(dsn=None):
    engine = sa.create_engine(dsn or connect_str)
    metadata.drop_all(engine)
