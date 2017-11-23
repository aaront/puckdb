from aiohttp import web

from .views import index, game


def setup_routes(app: web.Application):
    app.router.add_get('/', index)
    app.router.add_get('/games', game.index, name='games')
