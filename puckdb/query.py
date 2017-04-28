from collections import namedtuple
from datetime import datetime, timedelta
from typing import List, Optional

from dateutil import rrule

from . import exceptions

Interval = namedtuple('Interval', ['start', 'end'])


class BaseQuery(object):
    def __init__(self):
        pass


class TeamQuery(BaseQuery):
    def __init__(self, name=None):
        super().__init__()
        self.name = name


class GameQuery(BaseQuery):
    min_date = datetime(2013, 1, 1)

    def __init__(self, from_date=None, to_date=None, team=None):
        """

        :type from_date: datetime
        :type to_date: datetime
        :type team: TeamQuery
        """
        super().__init__()
        to_date = to_date or datetime.utcnow()
        if from_date and to_date < from_date:
            raise exceptions.FilterException('to_date must be after from_date')
        if not from_date or from_date < self.min_date:
            self.from_date = self.min_date
        else:
            self.from_date = from_date
        self.to_date = to_date
        self.team = team

    @property
    def from_season(self) -> Optional[int]:
        if not self.from_date:
            return None
        return self.from_date.year if self.from_date.month >= 9 else self.from_date.year - 1

    @property
    def to_season(self) -> Optional[int]:
        if not self.to_date:
            return None
        return self.to_date.year - 1 if self.to_date.month < 9 else self.to_date.year

    @property
    def intervals(self) -> List[Interval]:
        ints = []
        split_dates = list(rrule.rrule(rrule.DAILY, dtstart=self.from_date, until=self.to_date))
        if len(split_dates) >= 300:
            split_dates = list(rrule.rrule(rrule.MONTHLY, dtstart=self.from_date, until=self.to_date))
        elif len(split_dates) >= 60:
            split_dates = list(rrule.rrule(rrule.WEEKLY, dtstart=self.from_date, until=self.to_date))
        for i, start in enumerate(split_dates):
            if len(split_dates) > i + 1:
                end = split_dates[i + 1] - timedelta(days=1)
            else:
                end = start
            ints.append(Interval(start=start, end=end))
        return ints

    def by_season(self) -> List[str]:
        seasons = []
        for i in range(self.to_season - self.from_season + 1):
            season_start = self.from_season + i
            seasons.append('{}{}'.format(season_start, season_start + 1))
        return seasons
