import aiohttp
import pytest
from datetime import datetime

from puckdb.extern import nhl


@pytest.fixture(scope='function')
def session(event_loop):
    with aiohttp.ClientSession(loop=event_loop) as session:
        yield session


class TestNhl:
    @pytest.mark.asyncio
    async def test_get_teams(self, session: aiohttp.ClientSession):
        teams = await nhl.get_teams(session)
        assert len(teams) >= 30

    @pytest.mark.asyncio
    async def test_get_schedule_games(self, session: aiohttp.ClientSession):
        date = datetime(2016, 2, 23)
        games = await nhl.get_schedule_games(date, date, session)
        assert len(games) == 9
        assert 'gamePk' in games[0]
        assert games[0]['gamePk'] == 2015020893

    @pytest.mark.asyncio
    async def test_get_live_data(self, session: aiohttp.ClientSession):
        live = await nhl.get_live_data(2016021207, session)
        assert 'gameData' in live
        assert live['gamePk'] == 2016021207
        assert live['gameData']['teams']['away']['abbreviation'] == 'NYR'
        assert live['gameData']['teams']['home']['abbreviation'] == 'OTT'
