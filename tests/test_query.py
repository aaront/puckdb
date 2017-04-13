from datetime import datetime

import pytest

from puckdb import query, exceptions


class TestGameQuery:
    def test_one_season_range(self):
        from_date = datetime(2014, 10, 22)
        to_date = datetime(2015, 4, 1)
        game_query = query.GameQuery(from_date=from_date, to_date=to_date)
        seasons = game_query.by_season()
        assert len(seasons) == 1
        assert seasons[0] == '20142015'

    def test_season_before_range(self):
        from_date = datetime(2014, 4, 22)
        to_date = datetime(2015, 4, 1)
        game_query = query.GameQuery(from_date=from_date, to_date=to_date)
        seasons = game_query.by_season()
        assert len(seasons) == 2
        assert seasons[0] == '20132014'
        assert seasons[1] == '20142015'

    def test_season_after_range(self):
        from_date = datetime(2014, 10, 22)
        to_date = datetime(2015, 9, 1)
        game_query = query.GameQuery(from_date=from_date, to_date=to_date)
        seasons = game_query.by_season()
        assert len(seasons) == 2
        assert seasons[0] == '20142015'
        assert seasons[1] == '20152016'

    def test_season_min(self):
        to_date = datetime(2014, 10, 22)
        game_query = query.GameQuery(to_date=to_date)
        seasons = game_query.by_season()
        assert len(seasons) >= 2

    def test_season_max(self):
        from_date = datetime(2014, 10, 22)
        game_query = query.GameQuery(from_date=from_date)
        seasons = game_query.by_season()
        assert len(seasons) >= 2

    def test_days(self):
        from_date = datetime(2015, 10, 22)
        to_date = datetime(2015, 10, 30)
        game_query = query.GameQuery(from_date=from_date, to_date=to_date)
        days = game_query.intervals
        assert len(days) == 9
        assert days[0].start == datetime(2015, 10, 22)
        assert days[0].end == datetime(2015, 10, 22)

    def test_weeks(self):
        from_date = datetime(2015, 10, 22)
        to_date = datetime(2016, 2, 23)
        game_query = query.GameQuery(from_date=from_date, to_date=to_date)
        weeks = game_query.intervals
        assert len(weeks) == 18
        assert weeks[0].start == datetime(2015, 10, 22)
        assert weeks[0].end == datetime(2015, 10, 28)

    def test_months(self):
        from_date = datetime(2013, 10, 22)
        to_date = datetime(2016, 2, 23)
        game_query = query.GameQuery(from_date=from_date, to_date=to_date)
        months = game_query.intervals
        assert len(months) == 29
        assert months[0].start == datetime(2013, 10, 22)
        assert months[0].end == datetime(2013, 11, 21)

    def test_to_date_before_from_date(self):
        from_date = datetime(2016, 2, 23)
        to_date = datetime(2013, 10, 22)
        with pytest.raises(exceptions.FilterException):
            query.GameQuery(from_date=from_date, to_date=to_date)
