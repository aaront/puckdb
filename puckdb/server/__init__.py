import asyncio

from aiohttp import web

from .routes import setup_routes
from ..db import get_pool


async def init():
    app = web.Application()
    app['pool'] = await get_pool()
    setup_routes(app)
    return app


def run(loop=asyncio.get_event_loop()):
    app = loop.run_until_complete(init())
    web.run_app(app)
