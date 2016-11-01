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
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/50.0.2661.86 Safari/537.36'}


class BaseScraper(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, filter_by: filters.BaseFilter = None, concurrency: int = 5,
                 loop: asyncio.AbstractEventLoop = None, save: bool = True):
        self.filter_by = filter_by
        self.concurrency = concurrency
        self.loop = loop or asyncio.get_event_loop()
        self.sem = asyncio.Semaphore(concurrency, loop=self.loop)
        self.save = save

    async def _process_and_save(self, data : dict) -> List[dict]:
        data = await self._process(data)
        if self.save:
            await self._save(data)
        return data

    @abc.abstractmethod
    async def _save(self, data: List[dict]):
        pass

    async def _process(self, data: dict) -> List[dict]:
        return [data]

    async def _fetch(self, session: aiohttp.ClientSession, url: str) -> List[dict]:
        async with self.sem:
            async with session.get(url, headers=headers) as response:
                assert response.status == 200
                return await self._process_and_save(await response.json(loads=ujson.loads))

    @abc.abstractmethod
    def _get_tasks(self, session: aiohttp.ClientSession) -> List[asyncio.Future]:
        pass

    def save(self):
        with aiohttp.ClientSession(loop=self.loop) as session:
            self.loop.run_until_complete(self._get_tasks(session, True))

    def get(self):
        with aiohttp.ClientSession(loop=self.loop) as session:
            return list(itertools.chain(
                *self.loop.run_until_complete(asyncio.gather(*self._get_tasks(session), loop=self.loop))))


class TeamScraper(BaseScraper):
    url = 'https://statsapi.web.nhl.com/api/v1/teams/{team_id}'

    def __init__(self, filter_by: filters.BaseFilter = None, concurrency: int = 5,
                 loop: asyncio.AbstractEventLoop = None, save: bool = True):
        super().__init__(filter_by, concurrency, loop, save)

    async def _process(self, data: dict) -> List[dict]:
        return [data['teams'][0]]

    async def _save(self, data: List[dict]):
        pass

    def _get_tasks(self, session: aiohttp.ClientSession) -> List[asyncio.Future]:
        urls = [
            self.url.format(team_id=team_id) for team_id in range(1, 54)]
        return [asyncio.ensure_future(self._fetch(session, url), loop=self.loop) for url in urls]


class ScheduleScraper(BaseScraper):
    url = 'https://statsapi.web.nhl.com/api/v1/schedule?startDate={from_date}&endDate={to_date}' \
          '&expand=schedule.teams&site=en_nhl&teamId='

    def __init__(self, filter_by: filters.GameFilter, concurrency: int = 5, loop: asyncio.AbstractEventLoop = None,
                 save: bool = True):
        super().__init__(filter_by, concurrency, loop, save)

    async def _process(self, data: dict) -> List[dict]:
        games = []
        if 'dates' in data:
            for daily in data['dates']:
                games.extend(daily['games'])
        return games

    async def _save(self, data: List[dict]):
        pass

    def _get_tasks(self, session: aiohttp.ClientSession) -> List[asyncio.Future]:
        urls = [
            self.url.format(from_date=interval.start.strftime('%Y-%m-%d'), to_date=interval.end.strftime('%Y-%m-%d'))
            for interval in self.filter_by.intervals]
        return [asyncio.ensure_future(self._fetch(session, url), loop=self.loop) for url in urls]


class GameScraper(BaseScraper):
    url = 'https://statsapi.web.nhl.com/api/v1/game/{game_id}/feed/live'

    def __init__(self, filter_by: filters.GameFilter, concurrency: int = 3, loop: asyncio.AbstractEventLoop = None,
                 save: bool = True):
        super().__init__(filter_by, concurrency, loop, save)

    async def _save(self, data: List[dict]):
        pass

    def _get_tasks(self, session: aiohttp.ClientSession) -> List[asyncio.Future]:
        schedule_games = ScheduleScraper(self.filter_by, loop=self.loop).get()
        urls = [self.url.format(game_id=g['gamePk']) for g in schedule_games]
        return [asyncio.ensure_future(self._fetch(session, url), loop=self.loop) for url in urls]
