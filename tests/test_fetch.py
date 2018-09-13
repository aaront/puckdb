import asyncio
import os
from datetime import datetime

import pytest
import sqlalchemy as sa
from asyncpg.pool import Pool

from puckdb import db, fetch
from puckdb.db import get_connection_str, metadata

db_name = os.getenv('PUCKDB_DB_TEST_DATABASE', os.getenv('PUCKDB_DB_DATABASE'))


@pytest.fixture(scope='function')
async def pool():
    return await db.get_pool(database=db_name)


@pytest.fixture(scope='function')
def database(event_loop: asyncio.AbstractEventLoop, pool: Pool):
    engine = sa.create_engine(get_connection_str(db_name))
    metadata.drop_all(engine)
    metadata.create_all(engine)
    yield engine
    metadata.drop_all(engine)


@pytest.fixture(scope='function')
async def database_teams(event_loop: asyncio.AbstractEventLoop, database, pool: Pool):
    await fetch.get_teams(pool=pool)
    yield database


class TestFetch:
    @pytest.mark.asyncio
    async def test_get_games(self, database_teams, pool):
        date = datetime(2016, 2, 23)
        games = await fetch.get_games(from_date=date, to_date=date, pool=pool)
        assert games is not None
        assert len(games) == 9

    @pytest.mark.asyncio
    async def test_get_game(self, database_teams, pool):
        live = await fetch.get_game(2016021207, pool=pool)
        assert live.id == 2016021207
        assert live.version == 20170920092415
        assert live.season == 20162017
        assert live.type == 'regular'
        assert live.home == 9
        assert live.away == 3
        assert live.first_star == 8473544
        assert live.second_star == 8476419
        assert live.third_star == 8474884

    @pytest.mark.asyncio
    async def test_get_playoff_game(self, database_teams, pool):
        live = await fetch.get_game(2016030313, pool=pool)
        assert live.id == 2016030313
        assert live.season == 20162017
        assert live.type == 'playoff'
        assert live.home == 9
        assert live.away == 5
        assert live.first_star == 8467950
        assert live.second_star == 8471676
        assert live.third_star == 8470602

    @pytest.mark.asyncio
    async def test_get_teams(self, database, pool):
        teams = await fetch.get_teams(pool=pool)
        assert teams is not None
        assert len(teams) == 81
