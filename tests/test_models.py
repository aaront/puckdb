import unittest

from puckdb import models
from puckdb.models import EventType


class TestModelEvents(unittest.TestCase):
    def test_type_parser(self):
        self.assertEqual(EventType.blocked_shot, models.Event.parse_type('BLOCKED_SHOT'))
        self.assertEqual(EventType.shot, models.Event.parse_type('SHOT'))
        self.assertEqual(EventType.unknown, models.Event.parse_type('GAME_SCHEDULED')) # not tracked
        self.assertEqual(EventType.unknown, models.Event.parse_type('NON_SENSE'))
