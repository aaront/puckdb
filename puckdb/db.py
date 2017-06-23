import asyncio
import os
from typing import List

import sqlalchemy as sa
from asyncpgsa import pg
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import Table
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.sql import Insert

from . import model

metadata = sa.MetaData()

load_dotenv(find_dotenv())

pg_host = os.getenv('PUCKDB_DB_HOST')
pg_port = int(os.getenv('PUCKDB_DB_PORT'))
pg_database = os.getenv('PUCKDB_DB_DATABASE')
pg_user = os.getenv('PUCKDB_DB_USER')
pg_pass = os.getenv('PUCKDB_DB_PASSWORD')

connect_str = 'postgres://{user}:{passwd}@{host}:{port}/{database}'.format(user=pg_user, passwd=pg_pass, host=pg_host,
                                                                           port=pg_port, database=pg_database)

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


async def setup(loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()):
    await pg.init(
        loop=loop,
        host=pg_host,
        port=pg_port,
        database=pg_database,
        user=pg_user,
        password=pg_pass,
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
