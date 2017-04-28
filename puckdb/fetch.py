import asyncio
from datetime import datetime

import aiohttp
from asyncpgsa import pg

from . import db, parsers, model
from .extern import nhl

player_schema = model.PlayerSchema()
team_schema = model.TeamSchema()


async def get_game(game_id: int, sem: asyncio.Semaphore = asyncio.Semaphore(),
                   loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()):
    async with sem:
        async with aiohttp.ClientSession(loop=loop) as session:
            game_data = await nhl.get_live_data(game_id=game_id, session=session)
        return await _save_game(game_data)


async def _save_game(game: dict):
    game_data = game['gameData']
    game_id = game['gamePk']
    game_obj = parsers.game(game)
    for _, player in game_data['players'].items():
        await db.upsert(db.player_tbl, player_schema.dump(parsers.player(player)).data, True)
    await db.upsert(db.game_tbl, game_obj, True)
    await pg.fetchrow(db.event_tbl.delete().where(db.event_tbl.c.game == game_id))
    for event in game['liveData']['plays']['allPlays']:
        ev = parsers.event(game['gamePk'], event)
        if ev is None:
            continue
        await pg.fetchrow(db.event_tbl.insert().values(**ev))
    return game_obj


async def get_teams(loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()):
    async with aiohttp.ClientSession(loop=loop) as session:
        teams = await nhl.get_teams(session)
    team_objs = [team_schema.dump(parsers.team(team)).data for team in teams]
    for team in team_objs:
        await db.upsert(db.team_tbl, team)
    return team_objs


async def get_games(from_date: datetime, to_date: datetime, concurrency: int = 4,
                    loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()):
    async with aiohttp.ClientSession(loop=loop) as session:
        schedule = await nhl.get_schedule_games(from_date=from_date, to_date=to_date, session=session)
    semaphore = asyncio.Semaphore(concurrency)
    results = await asyncio.gather(*[get_game(game['gamePk'], sem=semaphore, loop=loop) for game in schedule],
                                   loop=loop)
    return results
