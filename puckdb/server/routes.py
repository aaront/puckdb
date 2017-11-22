from aiohttp import App

from .models import game


def setup_routes(app: App):
    app.router.add_get('/')