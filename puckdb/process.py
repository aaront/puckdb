import abc

from . import filters


class BaseProcessor(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def process(self, data):
        pass

    @abc.abstractmethod
    def get_urls(self, filter_by: filters.BaseFilter):
        pass


class NHLGameProcessor(BaseProcessor):
    url = 'https://statsapi.web.nhl.com/api/v1/schedule?startDate={from_date}&endDate={to_date}' \
          '&expand=schedule.teams,schedule.linescore,schedule.broadcasts.all,schedule.ticket,schedule.game.content' \
          '.media.epg&leaderCategories=&site=en_nhl&teamId='

    def process(self, data):
        pass

    def get_urls(self, filter_by: filters.GameFilter):
        return [self.url.format(from_date=day, to_date=day) for day in filter_by.intervals]
