import asyncio
import unittest
from datetime import datetime

from puckdb import filters, scrapers


class TestAsyncScraper(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)

    def tearDown(self):
        pass


class TestScheduleScraper(TestAsyncScraper):
    def test_one_day(self):
        day = datetime(2016, 4, 30)
        game_filter = filters.GameFilter(from_date=day, to_date=day)
        games = scrapers.NHLGameScraper(game_filter, loop=self.loop).get()
        self.assertEqual(2, len(games))


class TestTeamScraper(TestAsyncScraper):
    def test_get_teams(self):
        teams = scrapers.NHLTeamScraper(loop=self.loop).get()
        self.assertEqual(53, len(teams))
