from aiohttp import web
from .routes import setup_routes
import jinja2
import aiohttp_jinja2


async def create_app(config: dict):
    app = web.Application()
    app['config'] = config
    aiohttp_jinja2.setup(
        app,
        loader=jinja2.PackageLoader('cardsstore', 'templates')
    )
    setup_routes(app)
    return app
