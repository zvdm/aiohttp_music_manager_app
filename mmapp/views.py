import datetime
import os
import aiohttp_jinja2
from aiohttp import web
from pathlib import Path

from .db import get_user_by_api_key, get_user_albums_by_api_key, get_user_tracks_by_api_key, delete_user, \
    create_track, delete_track, get_track_item, get_user_albums_by_id_and_api_key
from .forms import validate_user_form, validate_track_form

routes = web.RouteTableDef()
BASE_DIR = Path(__file__).parent.parent
upload_path = BASE_DIR / 'mmapp' / 'uploads'


@routes.view('/')
class Index(web.View):
    async def get(self):
        return web.HTTPPermanentRedirect('/user')


@routes.view('/user')
class User(web.View):
    @aiohttp_jinja2.template('user_detail.html')
    async def get(self):
        api_key = self.request.cookies['api_key']
        # Get user by api_key from request cookie
        user = await get_user_by_api_key(self.request, api_key)
        # Get user's albums by user's id
        albums = await get_user_albums_by_api_key(self.request, user[0])
        # Get user's tracks by user's id
        tracks = await get_user_tracks_by_api_key(self.request, user[0])
        print('albums for user page', albums)
        print('tracks for user page', tracks)
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
        # Check if marker is delete user
        if 'delete' in data:
            result = await delete_user(self.request)
            print('DELETE USER', result)
            return web.HTTPSeeOther('/')
        # Else update information about user
        result = await validate_user_form(self.request, data)
        print(result)
        return web.HTTPSeeOther('/user')


@routes.view('/albums')
class Albums(web.View):
    @aiohttp_jinja2.template('album_detail.html')
    async def get(self):
        api_key = self.request.cookies['api_key']
        # Get user by api_key from request cookie
        user = await get_user_by_api_key(self.request, api_key)
        # Get user's tracks by user's id
        tracks = await get_user_tracks_by_api_key(self.request, user[0])
        return {
            'user': user[1],
            'albums': tracks,
        }

    async def post(self):
        data = await self.request.post()
        # Check if marker is delete track
        if 'delete' in data:
            user = await get_user_by_api_key(self.request, self.request.cookies['api_key'])
            result = await delete_track(self.request, int(data['delete']), user['id'])
            print('DELETE TRACK', result)
            return web.HTTPSeeOther('/tracks')


@routes.view('/tracks')
class Tracks(web.View):
    @aiohttp_jinja2.template('track_detail.html')
    async def get(self):
        api_key = self.request.cookies['api_key']
        # Get user by api_key from request cookie
        user = await get_user_by_api_key(self.request, api_key)
        # Get user's tracks by user's id
        tracks = await get_user_tracks_by_api_key(self.request, user[0])
        return {
            'user': user[1],
            'tracks': tracks,
        }

    async def post(self):
        data = await self.request.post()
        # Check if marker is delete track
        if 'delete' in data:
            user = await get_user_by_api_key(self.request, self.request.cookies['api_key'])
            result = await delete_track(self.request, int(data['delete']), user['id'])
            print('DELETE TRACK', result)
            return web.HTTPSeeOther('/tracks')


@routes.view(r'/track/{title:\w+.mp3}')
class TrackItem(web.View):
    @aiohttp_jinja2.template('track_item_detail.html')
    async def get(self):
        api_key = self.request.cookies['api_key']
        # Get track name from url
        title = self.request.match_info['title']
        # Get user by api_key from request cookie
        user = await get_user_by_api_key(self.request, api_key)
        # Check that this track exists in db
        track = await get_track_item(self.request, title, user['id'])
        albums = await get_user_albums_by_id_and_api_key(self.request, track['album_id'], user['id'])
        return {
            'user': user[1],
            'title': track['title'],
            'albums': albums
        }

    async def post(self):
        data = await self.request.post()
        old_title = self.request.match_info['title']

        # Update track title
        row = await validate_track_form(self.request, data['title'], old_title, upload_path)
        # print(result)
        return web.HTTPSeeOther(f'/track/{data["title"]}')


@routes.post('/track/upload')
async def track_upload(request):
    reader = await request.multipart()
    field = await reader.next()
    assert field.name == 'mp3'
    filename = field.filename
    if not filename.endswith('.mp3'):
        return web.HTTPSeeOther('/track')

    size = 0
    user = await get_user_by_api_key(request, request.cookies['api_key'])
    filename_for_dir = f'{user["id"]}-{filename}'
    saved_dir = os.path.join(upload_path, filename_for_dir)
    with open(saved_dir, 'wb') as f:
        while True:
            chunk = await field.read_chunk()
            if not chunk:
                break
            size += len(chunk)
            f.write(chunk)

    date_time = datetime.datetime.now()
    result = await create_track(request, filename, date_time, saved_dir, user[0])
    return web.HTTPSeeOther('/track')

# @routes.get(r'/{not_found:\d+}')
# async def not_found(request):
#     raise web.HTTPFound('/')
