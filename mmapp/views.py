import asyncpg
import hashlib
import uuid
import datetime
import aiohttp_jinja2
from aiohttp import web


routes = web.RouteTableDef()
salt = '3D4M'


@routes.view('/')
class Index(web.View):
    async def get(self):
        return web.HTTPPermanentRedirect('/login')


@routes.view('/login')
class Login(web.View):
    @aiohttp_jinja2.template('login.html')
    async def get(self):
        # session = await get_session(request)
        # print(session)
        var = self.request.app['config'].get('postgres')
        return {'variable': var}

    async def post(self):
        data = await self.request.post()
        print(data)
        if data.get('login', None) is not None and data.get('password', None) is not None:
            name = data.get('login')
            pwd = hashlib.sha256((data.get('password') + salt).encode()).hexdigest()
            try:
                async with self.request.app['db'].acquire() as conn:
                    row = await conn.fetchrow('SELECT name FROM Users WHERE name=$1 AND pwd=$2', name, pwd)
                    if row:
                        return web.Response(text=f"You have logged in as {row[0]}!")
            except Exception as e:
                print(e)
                pass
        if data.get('username', None) is not None and data.get('new_password', None) is not None:
            new_user = data.get('username')
            new_pwd = hashlib.sha256((data.get('new_password') + salt).encode()).hexdigest()
            # print(new_pwd)
            date_time = datetime.datetime.now()
            async with self.request.app['db'].acquire() as conn:
                row = await conn.execute('INSERT INTO Users'
                                         '(name, pwd, api_key, created_date, active_status)'
                                         'VALUES ($1,$2,$3,$4, $5)'
                                         'ON CONFLICT (name) DO NOTHING',
                                         new_user, new_pwd, uuid.uuid4(), date_time, True)
                # print(row)
                if not int(row.split()[2]):
                    return web.Response(text='This username is used yet. Please, try again')
                row = await conn.fetchrow('SELECT name,api_key FROM Users WHERE name=$1', new_user)
                # print(row[0], row[1])
                return web.Response(text=f"You have logged in as {row[0]}! Your api_key is {row[1]}")
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
