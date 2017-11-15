import asyncio
import os
import uuid
from datetime import datetime

import pytest

from puckdb import db, fetch


@pytest.fixture(scope='function')
def database(event_loop: asyncio.AbstractEventLoop):
    db_name = os.getenv('PUCKDB_DB_TEST_DATABASE', os.getenv('PUCKDB_DB_DATABASE'))
    event_loop.run_until_complete(db.setup(database=db_name))
    yield db.create(database=db_name)
    db.drop(database=db_name)


@pytest.fixture(scope='function')
def database_teams(event_loop: asyncio.AbstractEventLoop, database):
    event_loop.run_until_complete(fetch.get_teams())
    yield database


class TestFetch:
    @pytest.mark.asyncio
    async def test_get_games(self, database_teams):
        date = datetime(2016, 2, 23)
        games = await fetch.get_games(from_date=date, to_date=date)
        assert games is not None
        assert len(games) == 9

    @pytest.mark.asyncio
    async def test_get_game(self, database_teams):
        live = await fetch.get_game(2016021207)
        assert live['id'] == 2016021207
        assert live['version'] == 20170920092415
        assert live['season'] == 20162017
        assert live['type'] == 'regular'
        assert live['home'] == 9
        assert live['away'] == 3
        assert live['first_star'] == 8473544
        assert live['second_star'] == 8476419
        assert live['third_star'] == 8474884

    @pytest.mark.asyncio
    async def test_get_playoff_game(self, database_teams):
        live = await fetch.get_game(2016030313)
        assert live['id'] == 2016030313
        assert live['season'] == 20162017
        assert live['type'] == 'playoff'
        assert live['home'] == 9
        assert live['away'] == 5
        assert live['first_star'] == 8467950
        assert live['second_star'] == 8471676
        assert live['third_star'] == 8470602

    @pytest.mark.asyncio
    async def test_get_teams(self, database):
        teams = await fetch.get_teams()
        assert teams is not None
        assert len(teams) >= 30


