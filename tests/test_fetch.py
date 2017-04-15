import asyncio
from datetime import datetime

import pytest

from puckdb import db, fetch


@pytest.fixture(scope='function')
def database(event_loop: asyncio.AbstractEventLoop):
    event_loop.run_until_complete(db.setup(loop=event_loop))
    yield db.create()
    db.drop()


@pytest.fixture(scope='function')
def database_teams(event_loop: asyncio.AbstractEventLoop, database):
    event_loop.run_until_complete(fetch.get_teams(event_loop))
    yield database


class TestFetch:
    @pytest.mark.asyncio
    async def test_get_games(self, database_teams, event_loop: asyncio.AbstractEventLoop):
        date = datetime(2016, 2, 23)
        games = await fetch.get_games(from_date=date, to_date=date, loop=event_loop)
        assert games is not None
        assert len(games) == 9

    @pytest.mark.asyncio
    async def test_get_game(self, database_teams, event_loop: asyncio.AbstractEventLoop):
        live = await fetch.get_game(2016021207, loop=event_loop)
        assert live['id'] == 2016021207
        assert live['home'] == 9
        assert live['away'] == 3

    @pytest.mark.asyncio
    async def test_get_teams(self, database, event_loop: asyncio.AbstractEventLoop):
        teams = await fetch.get_teams(event_loop)
        assert teams is not None
        assert len(teams) >= 30


