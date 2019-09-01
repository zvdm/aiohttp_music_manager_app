import datetime
import aiohttp_jinja2
from aiohttp import web

from .db import get_user_by_api_key, get_user_albums_by_api_key, get_user_tracks_by_api_key
from .forms import validate_user_form

routes = web.RouteTableDef()


@routes.view('/')
class Index(web.View):
    async def get(self):
        return web.HTTPPermanentRedirect('/user')


@routes.view('/user')
class User(web.View):
    @aiohttp_jinja2.template('user_detail.html')
    async def get(self):
        api_key = self.request.cookies['api_key']
        print(api_key)
        # Get user by api_key from request cookie
        user = await get_user_by_api_key(self.request, api_key)
        # Get user's albums by user's id
        albums = await get_user_albums_by_api_key(self.request, user[0])
        # Get user's tracks by user's id
        tracks = await get_user_tracks_by_api_key(self.request, user[0])
        print('albums', albums)
        print('tracks', tracks)
        return {
            'user':
                {
                    'info': user,
                    'albums': albums,
                    'tracks': tracks
                }
        }

    async def post(self):
        data = await self.request.post()
        result = await validate_user_form(self.request, data)
        print(result)
        return web.HTTPSeeOther('/user')


@routes.view('/album')
class Album(web.View):
    async def get(self):
        return web.Response(text='I\'m working on this page Album')


@routes.view('/track')
class Track(web.View):
    async def get(self):
        return web.Response(text='I\'m working on this page "track"')


# @routes.get(r'/{not_found:\d+}')
# async def not_found(request):
#     raise web.HTTPFound('/')
