import enum
from typing import Type


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


def parse_enum(check_enum: Type[enum.Enum], type_str: str):
    for e in check_enum:
        if e.name == type_str.lower():
            return e
    raise ValueError('\'{}\' not found in enum'.format(type_str))
