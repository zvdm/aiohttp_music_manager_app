import asyncio
import asyncpg
import datetime
import jinja2
import aiohttp_jinja2
import uuid
from cryptography import fernet
from aiohttp import web
from aiohttp_session import setup, get_session, session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_security import authorized_userid

routes = web.RouteTableDef()


async def current_user_ctx_processor(request):
    userid = await authorized_userid(request)
    is_anonymous = not bool(userid)
    return {'current_user': {'is_anonymous': is_anonymous}}


@routes.view('/')
class Index(web.View):
    async def get(self):
        return web.HTTPPermanentRedirect('/login')


@routes.view('/login')
class Login(web.View):
    @aiohttp_jinja2.template('login.html')
    async def get(self):
        print(self.request.cookies)
        # session = await get_session(request)
        # print(session)
        return {'user': 'John', 'album': '/album'}

    async def post(self):
        data = await self.request.post()
        login = data['login']
        pwd = data['password']
        if login == 'user' and pwd == '1234':
            return web.Response(text="You have logged in")
        raise web.HTTPFound('/login')


@routes.view('/album')
class Album(web.View):
    async def get(self):
        return web.Response(text='I\'m working on this page')


@routes.view('/track')
class Track(web.View):
    async def get(self):
        return web.Response(text='I\'m working on this page "track"')


# @routes.get(r'/{not_found:\d+}')
# async def not_found(request):
#     raise web.HTTPFound('/')


app = web.Application()
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))
app['static_root_url'] = 'static'

app.add_routes(routes)


async def main():
    conn = await asyncpg.connect('postgresql://mmapp@localhost/mmappdb', password='mmapp1234')
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS Users(
            id SERIAL PRIMARY KEY, 
            name TEXT UNIQUE, 
            api_key UUID UNIQUE, 
            create_date TIMESTAMP,
            active_status BOOL
        );
        
        CREATE TABLE IF NOT EXISTS Albums(
            id SERIAL PRIMARY KEY,
            name TEXT,
            created_date TIMESTAMP,
            user_id INTEGER
        );
        
        CREATE TABLE IF NOT EXISTS Tracks(
            id SERIAL PRIMARY KEY,
            name TEXT,
            created_date TIMESTAMP,
            album_id INTEGER
        );
    ''')

    await conn.close()

asyncio.get_event_loop().run_until_complete(main())
web.run_app(app)
