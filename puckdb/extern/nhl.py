import itertools
import ujson
from datetime import datetime

import aiohttp

_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/50.0.2661.86 Safari/537.36'}

_BASE_URL = 'https://statsapi.web.nhl.com/api/v1'


async def get_teams(session: aiohttp.ClientSession):
    teams = await _get(_BASE_URL + '/teams', session)
    return teams['teams']


async def get_schedule_games(from_date: datetime, to_date: datetime, session: aiohttp.ClientSession):
    url = '/schedule?startDate={from_date}&endDate={to_date}&expand=schedule&site=en_nhl&teamId='.format(
        from_date=from_date.strftime('%Y-%m-%d'),
        to_date=to_date.strftime('%Y-%m-%d')
    )
    schedule = await _get(_BASE_URL + url, session)
    return list(itertools.chain.from_iterable([day['games'] for day in schedule['dates']]))


async def get_live_data(game_id: int, session: aiohttp.ClientSession):
    url = '/game/{game_id}/feed/live'.format(game_id=game_id)
    return await _get(_BASE_URL + url, session)


async def _get(url: str, session: aiohttp.ClientSession):
    async with session.get(url, headers=_HEADERS) as response:
        assert response.status == 200
        return await response.json(loads=ujson.loads)
