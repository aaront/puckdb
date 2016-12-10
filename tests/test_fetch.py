import asyncio
import unittest
from datetime import datetime

from puckdb import fetch
from puckdb.db import create, drop


class TestAsyncScraper(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        create()

    def tearDown(self):
        drop()


class TestFetch(TestAsyncScraper):
    def test_game_urls(self):
        date = datetime(2016, 2, 23)
        date_to = datetime(2016, 3, 1)
        games = fetch.games(date, date_to, loop=self.loop)
        # self.assertEqual(9, len(games))