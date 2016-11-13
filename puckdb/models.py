import enum
from datetime import datetime
from time import time
from typing import List


class GameState(enum.Enum):
    not_started = -1
    in_progress = 0
    finished = 1


class EventType(enum.Enum):
    unknown = -1
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
    on_goal = 0
    blocked = 1
    missed = 2


class Event(object):
    def __init__(self, game_id: int, team_id: int, type: EventType, time: time, x: float, y: float):
        self.game_id = game_id
        self.type = type
        self.time = time
        self.team_id = team_id
        self.x = x
        self.y = y

    @staticmethod
    def parse_type(type_str: str) -> EventType:
        for event_type in EventType:
            if event_type.name == type_str.lower():
                return event_type
        return EventType.unknown


class Shot(Event):
    def __init__(self, game_id: int, team_id: int, type: EventType, time: time, x: float, y: float, shot_type: ShotType):
        super().__init__(game_id, team_id, type, time, x, y)
        self.shot_type = shot_type


class Game(object):
    def __init__(self, id: int, season: int, status: GameState, away: int, home: int, start: datetime,
                 end: datetime, periods: int, events: List[Event]):
        self.id = id
        self.season = season
        self.status = status
        self.away = away
        self.home = home
        self.start = start
        self.end = end
        self.periods = periods
        self.events = events
