import asyncio
import enum

import abc
import os
from typing import List

import sqlalchemy as sa
from sqlalchemy import Table
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import Insert
from aiopg import sa as async_sa

metadata = sa.MetaData()

connect_str = os.getenv('PUCKDB_DATABASE', None)


class SkaterPosition(enum.Enum):
    center = 0
    left_wing = 1
    right_wing = 2
    defense = 3
    goalie = 4


class GameState(enum.Enum):
    not_started = -1
    in_progress = 0
    finished = 1


class EventType(enum.Enum):
    unknown = -1
    blocked_shot = 0
    challenge = 1
    faceoff = 2
    giveaway = 3
    goal = 4
    hit = 5
    missed_shot = 6
    penalty = 7
    shot = 8
    stop = 9
    takeaway = 10


class ShotAim(enum.Enum):
    on_goal = 0
    blocked = 1
    missed = 2


class ShotType(enum.Enum):
    backhand = 0
    deflected = 1
    slap = 2
    snap = 3
    tip = 4
    wrap_around = 5
    wrist = 6

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

team_tbl = sa.Table('team', metadata,
    sa.Column('id', sa.SmallInteger, primary_key=True),
    sa.Column('name', sa.String),
    sa.Column('team_name', sa.String),
    sa.Column('abbreviation', sa.String),
    sa.Column('city', sa.String)
)

skater_tbl = sa.Table('skater', metadata,
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('first_name', sa.String),
    sa.Column('last_name', sa.String),
    sa.Column('position', sa.Enum(SkaterPosition, name='skater_position'))
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
    def parse_type(type_str: str) -> EventType:
        for event_type in EventType:
            if event_type.name == type_str.lower():
                return event_type
        return EventType.unknown


class Team(DbModel):
    def __init__(self, data: dict):
        super(Team, self).__init__(team_tbl, data)

    def to_dict(self):
        return dict(
            name=self.data['name'],
            team_name=self.data['teamName'],
            abbreviation=self.data['abbreviation'],
            city=self.data['locationName']
        )