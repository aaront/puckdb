import unittest

from puckdb import db


class TestModelEvents(unittest.TestCase):
    def test_type_parser(self):
        self.assertEqual(db.EventType.blocked_shot, db.Event.parse_type('BLOCKED_SHOT'))
        self.assertEqual(db.EventType.shot, db.Event.parse_type('SHOT'))
        self.assertIsNone(db.Event.parse_type('GAME_SCHEDULED'))  # not tracked
        self.assertIsNone(db.Event.parse_type('NON_SENSE'))
