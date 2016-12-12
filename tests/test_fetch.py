import asyncio
import unittest
from datetime import datetime

from puckdb import db, fetch


class TestAsyncScraper(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        db.create()

    def tearDown(self):
        db.drop()


class TestFetch(TestAsyncScraper):
    def test_game_urls(self):
        date = datetime(2016, 2, 23)
        games = fetch.games(date, date, loop=self.loop)
        # TODO: Look up games from DB
        # self.assertEqual(9, len(games))
