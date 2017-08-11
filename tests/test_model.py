import pytest

from puckdb import model


class TestModelEvents:
    def test_type_parser(self):
        assert model.EventType.blocked_shot == model.parse_enum(model.EventType, 'BLOCKED_SHOT')
        assert model.EventType.shot == model.parse_enum(model.EventType, 'SHOT')
        with pytest.raises(ValueError) as excinfo:
            model.parse_enum(model.EventType, 'GAME_SCHEDULED') # not currently tracked
        with pytest.raises(ValueError) as excinfo:
            model.parse_enum(model.EventType, 'NON_SENSE')
