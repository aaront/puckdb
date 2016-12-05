import abc
from collections import namedtuple
from datetime import datetime, timedelta
from typing import List, Optional, Iterator

from dateutil import rrule
import requests
import ujson

from . import exceptions

from . import db

Interval = namedtuple('Interval', ['start', 'end'])

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/50.0.2661.86 Safari/537.36'}

SCHEDULE_URL = ('https://statsapi.web.nhl.com/api/v1/schedule?startDate={from_date}&endDate={to_date}'
                '&expand=schedule.teams&site=en_nhl&teamId=')
TEAM_URL = 'https://statsapi.web.nhl.com/api/v1/teams/{team_id}'
GAME_URL = 'https://statsapi.web.nhl.com/api/v1/game/{game_id}/feed/live'


class BaseQuery(object):
    def __init__(self, db_model: db.DbModel):
        self.db_model = db_model

    @abc.abstractproperty
    def urls(self) -> Iterator[str]:
        pass

    @abc.abstractmethod
    def get_insert_sql(self):
        pass


class TeamQuery(BaseQuery):
    def __init__(self, name=None):
        self.name = name
        super().__init__(db.Team)

    @property
    def urls(self) -> Iterator[str]:
        for team_id in range(1, 55):
            yield TEAM_URL.format(team_id=team_id)

    def get_insert_sql(self):
        pass


class GameQuery(BaseQuery):
    def __init__(self, from_date=None, to_date=None, team=None):
        """

        :type from_date: datetime
        :type to_date: datetime
        :type team: TeamQuery
        """
        to_date = to_date or datetime.utcnow()
        if from_date and to_date < from_date:
            raise exceptions.FilterException('to_date must be after from_date')
        self.from_date = from_date
        self.to_date = to_date
        self.team = team
        super().__init__(db.Game)

    @property
    def urls(self):
        for game_id in self._get_ids():
            yield GAME_URL.format(game_id=game_id)

    def _get_ids(self):
        url = SCHEDULE_URL.format(
            from_date=self.from_date.strftime('%Y-%m-%d'),
            to_date=self.to_date.strftime('%Y-%m-%d'))
        schedule = ujson.loads(requests.get(url, headers=HEADERS).text)
        for day in schedule['dates']:
            for game in day['games']:
                yield game['gamePk']

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
