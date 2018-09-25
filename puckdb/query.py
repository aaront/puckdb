import sqlalchemy as sa
from asyncpg.pool import Pool
from typing import Optional, List

from .db import team_tbl, game_tbl


class IdQuery:
    def __init__(self, conn: Pool, tbl: sa.Table) -> None:
        self.conn = conn
        self.tbl = tbl

    async def get(self, id: int):
        return await self.conn.fetchrow(self.tbl.select().where(self.tbl.c.id == id))

    async def get_all(self, ids: Optional[List[int]]):
        if ids:
            return self.conn.fetch(self.tbl.select(self.tbl.c.id.in_(ids)))
        return self.conn.fetch(self.tbl.select())


class TeamQuery(IdQuery):
    def __init__(self, conn: Pool) -> None:
        super().__init__(conn, team_tbl)


class GameQuery(IdQuery):
    def __init__(self, conn: Pool) -> None:
        super().__init__(conn, game_tbl)
