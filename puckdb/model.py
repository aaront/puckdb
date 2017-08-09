import enum
from datetime import datetime
from typing import Type

from marshmallow import Schema, fields
from marshmallow_enum import EnumField


class PlayerPosition(enum.Enum):
    center = 0
    left_wing = 1
    right_wing = 2
    defenseman = 3
    goalie = 4


class GameState(enum.Enum):
    not_started = -1
    in_progress = 0
    finished = 1


class EventType(enum.Enum):
    blocked_shot = 0
    challenge = 1
    faceoff = 2
    giveaway = 3
    goal = 4
    hit = 5
    missed_shot = 6
    penalty = 7
    shot = 8
    stop = 9
    takeaway = 10


class ShotType(enum.Enum):
    backhand = 0
    deflected = 1
    slap = 2
    snap = 3
    tip = 4
    wrap_around = 5
    wrist = 6


class Team:
    def __init__(self, id: int, name: str, team_name: str, abbreviation: str, city: str):
        self.id = id
        self.name = name
        self.team_name = team_name
        self.abbreviation = abbreviation
        self.city = city


class TeamSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    team_name = fields.String()
    abbreviation = fields.String()
    city = fields.String()


class Player:
    def __init__(self, id: int, first_name: str, last_name: str, position: PlayerPosition):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.position = position


class PlayerSchema(Schema):
    id = fields.Integer()
    first_name = fields.String()
    last_name = fields.String()
    position = EnumField(PlayerPosition)


class Game:
    def __init__(self, id: id, home: Team, away: Team, start_date: datetime):
        self.id = id
        self.home = home
        self.away = away
        self.start_date = start_date


class Event:
    def __init__(self, id: int, game: Game, team: Team, type: EventType, date: datetime, period: int):
        self.id = id
        self.game = game
        self.team = team
        self.type = type
        self.date = date
        self.period = period


def parse_enum(check_enum: Type[enum.Enum], type_str: str):
    for e in check_enum:
        if e.name == type_str.lower():
            return e
    return None
