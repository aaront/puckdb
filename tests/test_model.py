from puckdb import model


class TestModelEvents:
    def test_type_parser(self):
        assert model.EventType.blocked_shot == model.parse_enum(model.EventType, 'BLOCKED_SHOT')
        assert model.EventType.shot == model.parse_enum(model.EventType, 'SHOT')
        assert model.parse_enum(model.EventType, 'GAME_SCHEDULED') is None  # not tracked
        assert model.parse_enum(model.EventType, 'NON_SENSE') is None
