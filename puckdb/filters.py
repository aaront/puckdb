from datetime import datetime

from . import exceptions


class BaseFilter(object):
    pass


class TeamFilter(BaseFilter):
    def __init__(self, name=None):
        self.name = name


class GameFilter(BaseFilter):
    def __init__(self, from_date=None, to_date=None, team=None):
        """

        :type from_date: datetime
        :type to_date: datetime
        :type team: TeamFilter
        """
        if from_date is None:
            raise exceptions.FilterException('from_date must be provided')
        to_date = to_date or datetime.utcnow()
        if to_date < from_date:
            raise exceptions.FilterException('to_date must be after from_date')
        self.from_date = from_date
        self.to_date = to_date
        self.team = team

    @property
    def season_range(self):
        seasons = []
        from_season = self.from_date.year if self.from_date.month >= 9 else self.from_date.year - 1
        to_season = self.to_date.year - 1 if self.to_date.month < 9 else self.to_date.year
        for i in range(to_season - from_season + 1):
            season_start = from_season + i
            seasons.append('{}{}'.format(season_start, season_start+1))
        return seasons
