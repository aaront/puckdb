import unittest
from datetime import datetime

from puckdb import filters, scrapers


class TestScheduleScraper(unittest.TestCase):
    def test_one_day(self):
        day = datetime(2016, 4, 30)
        game_filter = filters.GameFilter(from_date=day, to_date=day)
        games = scrapers.fetch_games(game_filter)
        self.assertEqual(2, len(games))
