import asyncio
from typing import List, Optional

import abc
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


class DbModel(object):
    def __init__(self, table: Table, data: dict):
        self.table = table
        self.data = data

    @abc.abstractmethod
    def to_dict(self) -> dict:
        pass

    @property
    def upsert_sql(self) -> Insert:
        update = self.to_dict()
        insert_data = insert(self.table).values(
            **update
        )
        return insert_data.on_conflict_do_update(
            constraint=self.table.primary_key,
            set_=update
        )


class Game(DbModel):
    def __init__(self, data: dict):
        super().__init__(game_tbl, data)

    def to_dict(self):
        pass


class Event(DbModel):
    def __init__(self, data: dict):
        super(Event, self).__init__(event_tbl, data)

    def to_dict(self):
        pass

    @staticmethod
    def parse_type(type_str: str) -> Optional[model.EventType]:
        for event_type in model.EventType:
            if event_type.name == type_str.lower():
                return event_type
        return None

    @staticmethod
    def parse_shot_type(type_str: str) -> Optional[model.EventType]:
        for shot_type in model.ShotType:
            if shot_type.name == type_str.lower():
                return shot_type
        return None


class Team(DbModel):
    def __init__(self, data):
        super(Team, self).__init__(team_tbl, data)

    def to_dict(self):
        return dict(
            name=self.data['name'],
            team_name=self.data['teamName'],
            abbreviation=self.data['abbreviation'],
            city=self.data['locationName']
        )
