import asyncio
import ujson
from datetime import datetime
from typing import List, Iterable

import aiohttp
import requests
import tqdm

from . import db, parsers

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/50.0.2661.86 Safari/537.36'}
SCHEDULE_URL = ('https://statsapi.web.nhl.com/api/v1/schedule?startDate={from_date}&endDate={to_date}'
                '&expand=schedule.teams&site=en_nhl&teamId=')
GAME_URL = 'https://statsapi.web.nhl.com/api/v1/game/{game_id}/feed/live'


def games(from_date: datetime, to_date: datetime, concurrency: int = 5,
          loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()):
    sem = asyncio.Semaphore(concurrency, loop=loop)
    with aiohttp.ClientSession(loop=loop) as session:
        futures = [asyncio.ensure_future(_fetch(sem, session, url),
                                         loop=loop) for url in _get_game_urls(from_date, to_date)]
        loop.run_until_complete(_save_game(futures, loop=loop))


async def _save_game(tasks, loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()) -> Iterable[asyncio.Future]:
    for game_task in tqdm.tqdm(asyncio.as_completed(tasks, loop=loop), total=len(tasks)):
        game = await game_task
        game_data = game['gameData']
        upserts = []
        for _, team in game_data['teams'].items():
            upserts.append(db.upsert(db.team_tbl, parsers.team(team)))
        for _, player in game_data['players'].items():
            upserts.append(db.upsert(db.player_tbl, parsers.player(player)))
        await db.execute(upserts, loop=loop)


async def _fetch(sem: asyncio.Semaphore, session: aiohttp.ClientSession, url: str) -> List[dict]:
    async with sem:
        async with session.get(url, headers=HEADERS) as response:
            assert response.status == 200
            return await response.json(loads=ujson.loads)


def _get_game_urls(from_date: datetime, to_date: datetime):
    url = SCHEDULE_URL.format(
        from_date=from_date.strftime('%Y-%m-%d'),
        to_date=to_date.strftime('%Y-%m-%d'))
    schedule = ujson.loads(requests.get(url, headers=HEADERS).text)
    for day in schedule['dates']:
        for game in day['games']:
            yield GAME_URL.format(game_id=game['gamePk'])
