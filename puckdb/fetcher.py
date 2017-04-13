import asyncio
from datetime import datetime

import aiohttp

from . import db, parsers
from .extern import nhl

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


def get_games(from_date: datetime, to_date: datetime, concurrency: int = 10,
              loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()):
    loop.run_until_complete(GameFetcher(from_date, to_date, loop).run(concurrency))


class GameFetcher(object):
    def __init__(self, from_date: datetime, to_date: datetime, loop: asyncio.AbstractEventLoop):
        self.from_date = from_date
        self.to_date = to_date
        self.q = asyncio.Queue(loop=loop)
        self.loop = loop

    async def work(self, session: aiohttp.ClientSession):
        while True:
            game_data = await self.q.get()
            game = await nhl.get_live_data(game_data['gamePk'], session)
            await self._save(game)
            self.q.task_done()

    async def _save(self, game: dict):
        game_data = game['gameData']
        upserts = []
        for _, player in game_data['players'].items():
            upserts.append(db.upsert(db.player_tbl, parsers.player(player)))
        upserts.append(db.upsert(db.game_tbl, parsers.game(game), True))
        for event in game['liveData']['plays']['allPlays']:
            parsed_event = parsers.event(game['gamePk'], event)
            if parsed_event is None:
                continue
            upserts.append(db.upsert(db.event_tbl, parsed_event, True))
        # await db.execute(upserts, loop=self.loop)

    async def run(self, concurrency: int = 10):
        with aiohttp.ClientSession(loop=self.loop) as session:
            schedule_games = await nhl.get_schedule_games(self.from_date, self.to_date, session)
            for g in schedule_games:
                await self.q.put(g)
            workers = [asyncio.Task(self.work(session), loop=self.loop) for _ in range(concurrency)]
            await self.q.join()
            for w in workers:
                w.cancel()