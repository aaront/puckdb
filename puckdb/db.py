import asyncio
from typing import List

import os
import sqlalchemy as sa
from asyncpgsa import pg
from sqlalchemy import Table
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.sql import Insert

from . import model

metadata = sa.MetaData()

connect_str = os.getenv('PUCKDB_DATABASE', None)

game_tbl = sa.Table('game', metadata,
                    sa.Column('id', sa.BigInteger, primary_key=True),
                    sa.Column('away', sa.SmallInteger, sa.ForeignKey('team.id'), nullable=False),
                    sa.Column('home', sa.SmallInteger, sa.ForeignKey('team.id'), nullable=False),
                    sa.Column('date_start', sa.DateTime(timezone=True), index=True),
                    sa.Column('date_end', sa.DateTime(timezone=True), nullable=True)
                    )

team_tbl = sa.Table('team', metadata,
                    sa.Column('id', sa.SmallInteger, primary_key=True),
                    sa.Column('name', sa.String),
                    sa.Column('team_name', sa.String),
                    sa.Column('abbreviation', sa.String),
                    sa.Column('city', sa.String)
                    )

player_tbl = sa.Table('player', metadata,
                      sa.Column('id', sa.Integer, primary_key=True),
                      sa.Column('first_name', sa.String),
                      sa.Column('last_name', sa.String),
                      sa.Column('position', sa.Enum(model.PlayerPosition, name='player_position'))
                      )

event_tbl = sa.Table('event', metadata,
                     sa.Column('game', sa.BigInteger, sa.ForeignKey('game.id'), nullable=False, primary_key=True),
                     sa.Column('id', sa.Integer, nullable=False, primary_key=True),
                     sa.Column('team', sa.SmallInteger, sa.ForeignKey('team.id'), nullable=False),
                     sa.Column('type', sa.Enum(model.EventType, name='event_type'), nullable=False),
                     sa.Column('date', sa.DateTime(timezone=True), nullable=False),
                     sa.Column('shot_type', sa.Enum(model.ShotType, name='shot_type')),
                     sa.Column('period', sa.SmallInteger, nullable=False)
                     )


async def setup(dsn: str = connect_str, loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()):
    await pg.init(
        loop=loop,
        dsn=dsn,
        min_size=5,
        max_size=10
    )


async def insert(command_or_commands: Insert or List[Insert]):
    if not isinstance(command_or_commands, List):
        command_or_commands = [command_or_commands]
    for command in command_or_commands:
        await pg.fetchrow(command)


def create(dsn=None):
    engine = sa.create_engine(dsn or connect_str)
    metadata.drop_all(engine)
    metadata.create_all(engine)
    return engine


def drop(dsn=None):
    engine = sa.create_engine(dsn or connect_str)
    metadata.drop_all(engine)


async def upsert(table: Table, data: dict, update_on_conflict=False):
    insert_data = pg_insert(table).values(
        **data
    )
    if update_on_conflict:
        upsert_sql = insert_data.on_conflict_do_update(
            constraint=table.primary_key,
            set_=data
        )
    else:
        upsert_sql = insert_data.on_conflict_do_nothing(
            constraint=table.primary_key
        )
    await pg.fetchrow(upsert_sql)
