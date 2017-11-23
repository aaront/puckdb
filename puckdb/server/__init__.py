import asyncio

from aiohttp import web

from ..db import get_pool
from .routes import setup_routes


async def init():
    app = web.Application()
    app['pool'] = await get_pool()
    setup_routes(app)
    return app


def run(loop=asyncio.get_event_loop()):
    app = loop.run_until_complete(init())
    web.run_app(app)
