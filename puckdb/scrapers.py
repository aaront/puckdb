import abc
import asyncio
import itertools
import ujson
from typing import List

import aiohttp

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

from . import filters

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36'}


class BaseScraper(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, filter_by: filters.BaseFilter, concurrency: int = 5):
        self.filter_by = filter_by
        self.concurrency = concurrency
        self.sem = asyncio.Semaphore(concurrency)

    @abc.abstractmethod
    async def _process(self, data: dict) -> List[dict]:
        return [data]

    async def _fetch(self, session: aiohttp.ClientSession, url: str) -> List[dict]:
        async with self.sem:
            async with session.get(url, headers=headers) as response:
                assert response.status == 200
                return await self._process(await response.json(loads=ujson.loads))

    @abc.abstractmethod
    def _get_tasks(self, session: aiohttp.ClientSession) -> List[asyncio.Future]:
        pass

    def fetch(self, loop: asyncio.AbstractEventLoop):
        with aiohttp.ClientSession(loop=loop) as session:
            loop.run_until_complete(self._get_tasks(session))

    def get(self, loop: asyncio.AbstractEventLoop):
        with aiohttp.ClientSession(loop=loop) as session:
            return list(itertools.chain(*loop.run_until_complete(asyncio.gather(*self._get_tasks(session)))))


class NHLScheduleScraper(BaseScraper):
    url = 'https://statsapi.web.nhl.com/api/v1/schedule?startDate={from_date}&endDate={to_date}' \
          '&expand=schedule.teams&site=en_nhl&teamId='

    def __init__(self, filter_by: filters.GameFilter, concurrency: int = 5):
        super().__init__(filter_by, concurrency)

    async def _process(self, data: dict) -> List[dict]:
        games = []
        if 'dates' in data:
            for daily in data['dates']:
                games.extend(daily['games'])
        return games

    def _get_tasks(self, session: aiohttp.ClientSession) -> List[asyncio.Future]:
        urls = [
            self.url.format(from_date=interval.start.strftime('%Y-%m-%d'), to_date=interval.end.strftime('%Y-%m-%d'))
            for interval in self.filter_by.intervals]
        return [asyncio.ensure_future(self._fetch(session, url)) for url in urls]


class NHLGameScraper(BaseScraper):
    url = 'https://statsapi.web.nhl.com/api/v1/game/{game_id}/feed/live'

    def __init__(self, filter_by: filters.GameFilter, concurrency: int = 3):
        super().__init__(filter_by, concurrency)

    async def _process(self, data: dict) -> List[dict]:
        return [data]

    def _get_tasks(self, session: aiohttp.ClientSession) -> List[asyncio.Future]:
        urls = [self.url.format(game_id=gid) for gid in self.filter_by.game_ids]
        return [asyncio.ensure_future(self._fetch(session, url)) for url in urls]


def fetch_games(filter_by: filters.GameFilter) -> List[object]:
    loop = asyncio.get_event_loop()
    schedule_games = NHLScheduleScraper(filter_by).get(loop)
    game_filter = filters.GameFilter(game_ids=[g['gamePk'] for g in schedule_games])
    games = NHLGameScraper(game_filter).get(loop)
    loop.close()
    return games
