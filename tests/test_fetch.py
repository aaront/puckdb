import asyncio
from datetime import datetime

import pytest

from puckdb import db, fetcher


@pytest.fixture(scope='session')
def database():
    yield db.create()
    db.drop()


@pytest.fixture(scope='session')
def loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)
    yield loop


class TestFetch:
    def test_game_urls(self, database, loop):
        date = datetime(2016, 2, 23)
        games = fetcher.get_games(date, date, loop=loop)
        # TODO: Look up games from DB
        # assert len(games) == 9

    def test_get_teams(self, loop):
        teams = fetcher.get_teams(loop)
        # assert len(teams) >= 30
