import unittest
from datetime import datetime

from puckdb import filters, scrapers


class TestGameScraper(unittest.TestCase):
    def test_one_day(self):
        day = datetime(2016, 4, 30)
        game_filter = filters.GameFilter(from_date=day, to_date=day)
        game_scraper = scrapers.NHLGameScraper(game_filter)
        games = scrapers.fetch(game_scraper)
        self.assertEqual(2, len(games))