import json
import os
import pathlib
import pytest

from puckdb import parsers

game_data_path = pathlib.Path(__file__).parent.joinpath('data')
game_2016_id = 2016021207
with game_data_path.joinpath(f'game_{game_2016_id}.json').open('r') as f:
    game_2016 = json.load(f)


class TestParsers:
    def test_game(self):
        game = parsers.game(game_2016_id, 1, game_2016)
        assert game['id'] == 2016021207
