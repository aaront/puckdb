import abc
from datetime import datetime

import aiohttp

from . import exceptions, filters

class BaseScraper(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    async def get_schedule(self, game_filter: filters.GameFilter):
        pass


class NHLScraper(BaseScraper):
    schedule_url = 'http://live.nhl.com/GameData/SeasonSchedule-{season}.json'

    async def get_schedule(self, game_filter: filters.GameFilter):
        pass
