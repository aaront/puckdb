import enum


class GameState(enum.Enum):
    not_started = -1
    in_progress = 0
    finished = 1


class GameEvent(enum.Enum):
    shot = 0
    block = 1
    miss = 2
