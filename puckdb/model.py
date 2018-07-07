import enum
from datetime import datetime
from typing import Type, Optional

from dataclasses import dataclass


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


class GameType(enum.Enum):
    regular = 0
    playoff = 1


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


@dataclass
class Team():
    __slots__ = ['id', 'name', 'team_name', 'abbreviation', 'city']
    id: int
    name: str
    team_name: str
    abbreviation: str
    city: str


@dataclass
class Player():
    __slots__ = ['id', 'first_name', 'last_name', 'position']
    id: int
    first_name: str
    last_name: str
    position: str


@dataclass
class Game():
    __slots__ = ['id', 'version', 'season', 'type', 'away', 'home', 'date_start', 'date_end', 'first_star',
                 'second_star', 'third_star']
    id: int
    version: int
    season: int
    type: str
    away: int
    home: int
    date_start: datetime
    date_end: Optional[datetime]
    first_star: Optional[int]
    second_star: Optional[int]
    third_star: Optional[int]


def parse_enum(check_enum: Type[enum.Enum], type_str: str):
    for e in check_enum:
        if e.name == type_str.lower():
            return e
    raise ValueError('\'{}\' not found in enum'.format(type_str))
