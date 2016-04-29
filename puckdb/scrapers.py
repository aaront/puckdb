import abc

from . import filters


class BaseScraper(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    async def process(self, data):
        pass

    @abc.abstractmethod
    async def run(self, filter_by: filters.BaseFilter):
        pass


class NHLGameScraper(BaseScraper):
    url = 'https://statsapi.web.nhl.com/api/v1/schedule?startDate={from_date}&endDate={to_date}' \
          '&expand=schedule.teams,schedule.linescore,schedule.broadcasts.all,schedule.ticket,schedule.game.content' \
          '.media.epg&leaderCategories=&site=en_nhl&teamId='

    async def process(self, data):
        pass

    async def run(self, filter_by: filters.GameFilter):
        return [self.url.format(from_date=day, to_date=day) for day in filter_by.intervals]
