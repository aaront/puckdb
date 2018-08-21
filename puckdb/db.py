import os

import sqlalchemy as sa
from asyncpgsa import create_pool, pg
from dotenv import find_dotenv, load_dotenv
from sqlalchemy import Table
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.postgresql.dml import Insert

from . import model

metadata = sa.MetaData()

load_dotenv(find_dotenv())

pg_host = os.getenv('PUCKDB_DB_HOST')
pg_port = int(os.getenv('PUCKDB_DB_PORT', '5432'))
pg_database = os.getenv('PUCKDB_DB_DATABASE')
pg_user = os.getenv('PUCKDB_DB_USER')
pg_pass = os.getenv('PUCKDB_DB_PASSWORD')

player_tbl = sa.Table('player', metadata,
                      sa.Column('id', sa.Integer, primary_key=True),
                      sa.Column('first_name', sa.String),
                      sa.Column('last_name', sa.String),
                      sa.Column('position', sa.Enum(model.PlayerPosition, name='player_position')),
                      sa.Column('handedness', sa.Enum(model.PlayerHandedness, name='player_handedness')),
                      sa.Column('height', sa.Float),
                      sa.Column('weight', sa.SmallInteger),
                      sa.Column('captain', sa.Boolean),
                      sa.Column('alternate_captain', sa.Boolean),
                      sa.Column('birth_city', sa.String),
                      sa.Column('birth_country', sa.String),
                      sa.Column('birth_date', sa.Date),
                      sa.Column('birth_state_province', sa.String),
                      sa.Column('nationality', sa.String)
                      )

game_tbl = sa.Table('game', metadata,
                    sa.Column('id', sa.BigInteger, primary_key=True),
                    sa.Column('version', sa.BigInteger, primary_key=True),
                    sa.Column('season', sa.Integer, nullable=False),
                    sa.Column('type', sa.Enum(model.GameType, name='game_type')),
                    sa.Column('away', sa.SmallInteger, sa.ForeignKey('team.id'), nullable=False),
                    sa.Column('home', sa.SmallInteger, sa.ForeignKey('team.id'), nullable=False),
                    sa.Column('date_start', sa.DateTime(timezone=True), index=True),
                    sa.Column('date_end', sa.DateTime(timezone=True), nullable=True),
                    sa.Column('first_star', sa.Integer, sa.ForeignKey('player.id'), nullable=True),
                    sa.Column('second_star', sa.Integer, sa.ForeignKey('player.id'), nullable=True),
                    sa.Column('third_star', sa.Integer, sa.ForeignKey('player.id'), nullable=True)
                    )

team_tbl = sa.Table('team', metadata,
                    sa.Column('id', sa.SmallInteger, primary_key=True),
                    sa.Column('name', sa.String),
                    sa.Column('team_name', sa.String),
                    sa.Column('abbreviation', sa.String),
                    sa.Column('city', sa.String)
                    )

event_tbl = sa.Table('event', metadata,
                     sa.Column('game', sa.BigInteger, nullable=False, primary_key=True),
                     sa.Column('version', sa.BigInteger, primary_key=True),
                     sa.Column('id', sa.Integer, nullable=False, primary_key=True),
                     sa.Column('team', sa.SmallInteger, sa.ForeignKey('team.id'), nullable=False),
                     sa.Column('type', sa.Enum(model.EventType, name='event_type'), nullable=False),
                     sa.Column('date', sa.DateTime(timezone=True), nullable=False),
                     sa.Column('shot_type', sa.Enum(model.ShotType, name='shot_type')),
                     sa.Column('period', sa.SmallInteger, nullable=False),
                     sa.Column('location_x', sa.Float, nullable=True),
                     sa.Column('location_y', sa.Float, nullable=True),
                     sa.ForeignKeyConstraint(('game', 'version'), ['game.id', 'game.version'])
                     )


async def setup(database: str = None):
    await pg.init(
        host=pg_host,
        port=pg_port,
        database=database or pg_database,
        user=pg_user,
        password=pg_pass,
        min_size=5,
        max_size=10
    )


async def get_pool(database: str = None):
    return await create_pool(
        host=pg_host,
        port=pg_port,
        database=database or pg_database,
        user=pg_user,
        password=pg_pass,
        min_size=5,
        max_size=10
    )


def upsert(table: Table, data: dict, update_on_conflict: bool = False) -> Insert:
    insert_data = pg_insert(table).values(
        **data
    )
    if update_on_conflict:
        return insert_data.on_conflict_do_update(
            constraint=table.primary_key,
            set_=data
        )
    return insert_data.on_conflict_do_nothing(
        constraint=table.primary_key
    )


def drop(database: str = None):
    engine = sa.create_engine(get_connection_str(database))
    metadata.drop_all(engine)


def get_connection_str(database: str = None) -> str:
    return f'postgresql+pg8000://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{database or pg_database}'
