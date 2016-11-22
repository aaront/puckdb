import asyncio
import itertools
import ujson
from typing import List, Iterable

import abc
import aiohttp
import tqdm

from . import db

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

    async def _process_and_save(self, data: dict) -> List[dict]:
        data = await self._process(data)
        if self.save:
            insert_sql = self._insert_sql(data)
            if insert_sql:
                await db.execute(insert_sql, loop=self.loop)
        return data

    async def _process(self, data: dict) -> List[dict]:
        return [data]

    async def _fetch(self, session: aiohttp.ClientSession, url: str) -> List[dict]:
        async with self.sem:
            async with session.get(url, headers=headers) as response:
                assert response.status == 200
                return await self._process_and_save(await response.json(loads=ujson.loads))

    async def _wait_progress(self, session: aiohttp.ClientSession) -> Iterable[asyncio.Future]:
        tasks = self._get_tasks(session)
        for f in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks)):
            await f

    @abc.abstractmethod
    def _insert_sql(self, data: List[dict]) -> List[db.Insert]:
        pass

    @abc.abstractmethod
    def _get_tasks(self, session: aiohttp.ClientSession) -> List[asyncio.Task]:
        pass

    def fetch(self):
        with aiohttp.ClientSession(loop=self.loop) as session:
            self.loop.run_until_complete(self._wait_progress(session))

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

    def _insert_sql(self, data: List[dict]):
        team = data[0]
        return [db.team_tbl.insert().values(
            id=team['id'],
            name=team['name'],
            team_name=team['teamName'],
            abbreviation=team['abbreviation'],
            city=team['locationName']
        )]
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

    def _insert_sql(self, data: List[dict]):
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

    def _insert_sql(self, data: List[dict]):
        pass

    def _get_tasks(self, session: aiohttp.ClientSession) -> List[asyncio.Future]:
        schedule_games = ScheduleScraper(self.filter_by, loop=self.loop).get()
        urls = [self.url.format(game_id=g['gamePk']) for g in schedule_games]
        return [asyncio.ensure_future(self._fetch(session, url), loop=self.loop) for url in urls]
