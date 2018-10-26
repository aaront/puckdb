from abc import abstractmethod
from typing import List, Optional

import sqlalchemy as sa
from asyncpg.pool import Pool

from .db import event_tbl, game_tbl, player_tbl, team_tbl, upsert


class IdQuery:
    def __init__(self, conn: Pool, tbl: sa.Table) -> None:
        self.conn = conn
        self.tbl = tbl

    async def get(self, id: int):
        return await self.conn.fetchrow(self.tbl.select().where(self.tbl.c.id == id))

    async def get_all(self, ids: Optional[List[int]]):
        if ids:
            return await self.conn.fetch(self.tbl.select(self.tbl.c.id.in_(ids)))
        return await self.conn.fetch(self.tbl.select())

    @abstractmethod
    async def insert(self, data: dict):
        pass


class TeamQuery(IdQuery):
    def __init__(self, conn: Pool) -> None:
        super().__init__(conn, team_tbl)

    async def insert(self, data: dict):
        return await self.conn.fetchrow(upsert(self.tbl, data, True))


class GameQuery(IdQuery):
    def __init__(self, conn: Pool) -> None:
        super().__init__(conn, game_tbl)

    async def insert(self, data: dict):
        return await self.conn.fetchrow(upsert(self.tbl, data, True))


class PlayerQuery(IdQuery):
    def __init__(self, conn: Pool) -> None:
        super().__init__(conn, player_tbl)

    async def insert(self, data: dict):
        return await self.conn.fetchrow(upsert(self.tbl, data, True))


class EventQuery(IdQuery):
    def __init__(self, conn: Pool) -> None:
        super().__init__(conn, event_tbl)

    async def insert(self, data: dict):
        return await self.conn.fetchrow(upsert(self.tbl, data, False))
