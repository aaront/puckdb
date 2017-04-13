from puckdb import db, model


class TestModelEvents:
    def test_type_parser(self):
        assert model.EventType.blocked_shot == db.Event.parse_type('BLOCKED_SHOT')
        assert model.EventType.shot == db.Event.parse_type('SHOT')
        assert db.Event.parse_type('GAME_SCHEDULED') is None  # not tracked
        assert db.Event.parse_type('NON_SENSE') is None
