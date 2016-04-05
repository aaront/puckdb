import abc
from datetime import datetime

import asyncio
import aiohttp

from . import exceptions, filters


class BaseScraper(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, loop: asyncio.BaseEventLoop):
        self.loop = loop

    @abc.abstractmethod
    async def process(self, data):
        pass

    @abc.abstractmethod
    async def get(self, filter_by: filters.BaseFilter):
        pass


class NHLGameScraper(BaseScraper):
    url = 'https://statsapi.web.nhl.com/api/v1/schedule?startDate={from_date}&endDate={to_date}' \
          '&expand=schedule.teams,schedule.linescore,schedule.broadcasts.all,schedule.ticket,schedule.game.content' \
          '.media.epg&leaderCategories=&site=en_nhl&teamId='

    async def process(self, data):
        pass

    async def get(self, filter_by: filters.GameFilter):
        super().get(filter_by)
