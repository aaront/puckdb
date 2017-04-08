from datetime import datetime
import itertools

import aiohttp
import ujson

_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/50.0.2661.86 Safari/537.36'}

_BASE_URL = 'https://statsapi.web.nhl.com/api/v1'
SCHEDULE_URL = '/schedule?startDate={from_date}&endDate={to_date}&expand=schedule&site=en_nhl&teamId='
GAME_URL = '/game/{game_id}/feed/live'
TEAMS_URL = '/teams'

async def get_teams(session: aiohttp.ClientSession):
    return await _fetch('/teams', session)

async def get_schedule_games(from_date: datetime, to_date: datetime, session: aiohttp.ClientSession):
    url = '/schedule?startDate={from_date}&endDate={to_date}&expand=schedule&site=en_nhl&teamId='.format(
        from_date=from_date,
        to_date=to_date
    )
    schedule = await _fetch(url, session)
    return list(itertools.chain.from_iterable([day['games'] for day in schedule['dates']]))

async def get_live_data(game_id: int, session: aiohttp.ClientSession):
    url = '/game/{game_id}/feed/live'.format(game_id=game_id)
    return await _fetch(url, session)

async def _fetch(url: str, session: aiohttp.ClientSession):
    async with session.get(url, headers=_HEADERS) as response:
        assert response.status == 200
        return await response.json(loads=ujson.loads)
