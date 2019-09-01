import aiohttp_jinja2
import datetime
from aiohttp import web

from .db import get_user_by_api_key, user_login, user_signup


@web.middleware
async def check_api_key(request, handler):
    class SignUp(web.View):
        async def get(self):
            return aiohttp_jinja2.render_template('signup.html', self, {'url': self.path})

        async def post(self):
            data = await self.post()
            # Login existed user and return api_key as cookie
            if data.get('login', None) is not None \
                    and data.get('login', None) != '' \
                    and data.get('password', None) is not None\
                    and data.get('password', None) != '':
                try:
                    async with self.app['db'].acquire() as conn:
                        row = await user_login(conn, data.get('login'), data.get('password'))
                    if row:
                        res = web.HTTPSeeOther(self.path)
                        res.cookies['api_key'] = row
                        return res
                except:
                    e = 'Incorrect username or password'
                    print(e)
                    return aiohttp_jinja2.render_template('signup.html', self, {'error_login': e, 'url': request.path})
            # Sign up new user and return api_key as cookie
            if data.get('username', None) is not None \
                    and data.get('username', None) != '' \
                    and data.get('new_password', None) is not None\
                    and data.get('new_password', None) != '':
                print(data.get('new_password') == '')
                date_time = datetime.datetime.now()
                async with self.app['db'].acquire() as conn:
                    row = await user_signup(conn, data.get('username'), data.get('new_password'), date_time, True)
                if not row:
                    e = 'This username is used yet. Please, try again'
                    print(e)
                    return aiohttp_jinja2.render_template('signup.html', self, {'error_signup': e, 'url': request.path})
                res = web.HTTPSeeOther(self.path)
                res.cookies['api_key'] = row
                return res
            print('ERROR')
            e = 'Perhaps some field is not filled'
            return aiohttp_jinja2.render_template('signup.html', self, {'error': e, 'url': request.path})

    if request.headers.get('Cookie', None) is None:
        # No one cookie
        print('No one cookie, go to signup')
        if request.method == 'GET':
            print('GET', request.method)
            response = await SignUp.get(request)
        else:
            print('POST', request.method)
            response = await SignUp.post(request)
        print('Middleware login/signup is success', response)
        return response
    api_key = request.headers.get('Cookie').split('=')
    print('req_key', api_key[1])
    if api_key[0] == 'api_key' and await get_user_by_api_key(request, api_key[1]):
        # If cookie is in headers, check api_key
        response = await handler(request)
        return response
    print('Unexpected error')
    return check_api_key
