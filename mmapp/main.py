import sys
import asyncpgsa
import jinja2
import aiohttp_jinja2
from cryptography import fernet
from aiohttp import web
from aiohttp_session import setup, get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_security import authorized_userid

# from mmapp.settings import config
from mmapp.views import routes


# async def current_user_ctx_processor(request):
#     userid = await authorized_userid(request)
#     is_anonymous = not bool(userid)
#     return {'current_user': {'is_anonymous': is_anonymous}}


async def init_app(config):
    app = web.Application()

    app['config'] = config

    aiohttp_jinja2.setup(app, loader=jinja2.PackageLoader('mmapp', 'templates'))

    app['static_root_url'] = 'static'

    app.add_routes(routes)

    app.on_startup.append(on_start)
    app.on_cleanup.append(on_close)

    return app


async def create_app(config: dict):
    app = await init_app(config)
    return app
    # connection = asyncpg.connect('postgresql://mmapp:mmapp1234@localhost/mmappdb', password='mmapp1234')


async def on_start(app):
    config = app['config']
    app['db'] = await asyncpgsa.create_pool(dsn=config['database_uri'])


async def on_close(app):
    await app['db'].close()
