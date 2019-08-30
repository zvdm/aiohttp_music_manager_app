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
        conn = await asyncpg.connect('postgresql://mmapp@localhost/mmappdb', password='mmapp1234')
        if data.get('api_key', None) is not None:
            api_key = data.get('api_key')
            try:
                row = await conn.fetchrow('SELECT name FROM Users WHERE api_key=$1', api_key)
                if row:
                    await conn.close()
                    return web.Response(text=f"You have logged in as {row}!")
            except Exception as e:
                print(e)
                pass
        if data.get('username', None) is not None:
            new_user = data.get('username')
            date_time = datetime.datetime.now()
            row = await conn.execute('INSERT INTO Users'
                                     '(name, api_key, created_date, active_status)'
                                     'VALUES ($1,$2,$3,$4) '
                                     'ON CONFLICT (name) DO NOTHING',
                                     new_user, uuid.uuid4(), date_time, True)
            if int(row.split()[2]):
                await conn.close()
                return web.HTTPPermanentRedirect('/login', body='This user exists')
            row = await conn.fetchrow('SELECT name,api_key FROM Users WHERE name=$1', new_user)
            print(row[0], row[1])
            await conn.close()
            return web.Response(text=f"You have logged in as {new_user}!")
        await conn.close()
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
            created_date TIMESTAMP,
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
connection = asyncpg.connect('postgresql://mmapp@localhost/mmappdb', password='mmapp1234')