import asyncio
from datetime import datetime
from typing import List

import aiohttp
from asyncpg.pool import Pool

from . import db, parsers
from .extern import nhl


async def _download_game(game_id: int, session: aiohttp.ClientSession, pool: Pool = db.get_pool(), sem: asyncio.Semaphore = asyncio.Semaphore()):
    async with sem:
        game_data = await nhl.get_live_data(game_id=game_id, session=session)
        return await _save_game(game_data, pool=pool)


async def _save_game(game: dict, pool: Pool = db.get_pool()):
    async with pool.transaction() as conn:
        game_id = int(game['gamePk'])
        game_data = game['gameData']
        game_status = game_data['status']['abstractGameState']
        if game_status == 'Final':
            game_version = int(game['metaData']['timeStamp'])
        else:
            game_version = -1
        game_obj = parsers.game(game_id, game_version, game)
        for _, player in game_data['players'].items():
            await conn.fetchrow(db.upsert(db.player_tbl, parsers.player(player), True))
        await conn.fetchrow(db.upsert(db.game_tbl, game_obj, True))
        for event in game['liveData']['plays']['allPlays']:
            ev = parsers.event(game_id, game_version, event)
            if ev is None:
                continue
            await conn.fetchrow(db.upsert(db.event_tbl, ev))
    return game_obj


async def _get_games(game_ids: List[int], pool: Pool = db.get_pool()):
    g = db.game_tbl
    async with pool.acquire() as conn:
        for row in await conn.fetch(g.select(g.c.id.in_(game_ids))):
            yield dict(row)


async def get_game(game_id: int, pool: Pool = db.get_pool()):
    async with aiohttp.ClientSession() as session:
        return await _download_game(game_id, session, pool=pool)


async def get_teams(pool: Pool = db.get_pool()):
    async with aiohttp.ClientSession() as session:
        teams = await nhl.get_teams(session)
    team_objs = [parsers.team(team) for team in teams]
    async with pool.acquire() as conn:
        for team in team_objs:
            await conn.fetchrow(db.upsert(db.team_tbl, team))
    return team_objs


async def get_games(from_date: datetime, to_date: datetime, concurrency: int = 4, pool: Pool = db.get_pool()):
    semaphore = asyncio.Semaphore(concurrency)
    async with aiohttp.ClientSession() as session:
        schedule = await nhl.get_schedule_games(from_date=from_date, to_date=to_date, session=session)
        all_game_ids = [game['gamePk'] for game in schedule]
        existing_games = [g async for g in _get_games(all_game_ids, pool=pool)]
        need_download = set(all_game_ids) - set([game['id'] for game in existing_games])
        task = [_download_game(game_id, session=session, sem=semaphore, pool=pool) for game_id in need_download]
        results = await asyncio.gather(*task)
    results.extend(existing_games)
    return sorted(results, key=lambda k: k['id'])
