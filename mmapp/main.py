import asyncpgsa
import jinja2
import aiohttp_jinja2
from aiohttp import web

from .routes import setup_static_routes
from .views import routes
from .middlewares import check_api_key


# async def init_app(config):
async def init_app(config):
    app = web.Application(middlewares=[check_api_key])

    app['config'] = config

    aiohttp_jinja2.setup(app, loader=jinja2.PackageLoader('mmapp', 'templates'))

    app.add_routes(routes)

    setup_static_routes(app)

    app.on_startup.append(on_start)
    app.on_cleanup.append(on_close)

    return app


# async def create_app(config: dict):
async def create_app(config):
    # app = await init_app(config)
    app = await init_app(config)
    return app


async def on_start(app):
    config = app['config']
    app['db'] = await asyncpgsa.create_pool(dsn=config['database_uri'])


async def on_close(app):
    await app['db'].close()
