import asyncio
import ujson
from datetime import datetime

import aiohttp

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


def games(from_date: datetime, to_date: datetime, concurrency: int = 10,
          loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()):
    loop.run_until_complete(GameFetcher(from_date, to_date, loop, concurrency).run())


class GameFetcher(object):
    def __init__(self, from_date: datetime, to_date: datetime, loop: asyncio.AbstractEventLoop, concurrency: int = 10):
        self.from_date = from_date
        self.to_date = to_date
        self.concurrency = concurrency
        self.q = asyncio.Queue(loop=loop)
        self.loop = loop

    async def work(self, session: aiohttp.ClientSession):
        while True:
            url = await self.q.get()
            game = await self.fetch(url, session)
            await self._save(game)
            self.q.task_done()

    @staticmethod
    async def fetch(url: str, session: aiohttp.ClientSession):
        async with session.get(url, headers=HEADERS) as response:
            assert response.status == 200
            return await response.json(loads=ujson.loads)

    async def _get_game_urls(self, session: aiohttp.ClientSession, from_date: datetime, to_date: datetime):
        url = SCHEDULE_URL.format(
            from_date=from_date.strftime('%Y-%m-%d'),
            to_date=to_date.strftime('%Y-%m-%d'))
        schedule = await self.fetch(url, session)
        urls = []
        for day in schedule['dates']:
            for game in day['games']:
                urls.append(GAME_URL.format(game_id=game['gamePk']))
        return urls

    async def _save(self, game: dict):
        game_data = game['gameData']
        upserts = []
        for type, team in game_data['teams'].items():
            upserts.append(db.upsert(db.team_tbl, parsers.team(team)))
        for _, player in game_data['players'].items():
            upserts.append(db.upsert(db.player_tbl, parsers.player(player)))
        # upserts.append(db.upsert(db.game_tbl, parsers.game(game), True))
        await db.execute(upserts, loop=self.loop)

    async def run(self):
        with aiohttp.ClientSession(loop=self.loop) as session:
            urls = await self._get_game_urls(session, self.from_date, self.to_date)
            for url in urls:
                await self.q.put(url)
            workers = [asyncio.Task(self.work(session), loop=self.loop) for _ in range(self.concurrency)]
            await self.q.join()
            for w in workers:
                w.cancel()