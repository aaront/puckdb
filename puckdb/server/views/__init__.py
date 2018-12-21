from aiohttp import web


async def index():
    return web.Response(text='Hello World')
