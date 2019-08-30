import aiohttp
from aiohttp import web

# async def hello(request):
#     return web.Response(text="Hello, world")
#
# app = web.Application()
# app.add_routes([web.get('/', hello)])
#
# web.run_app(app)

routes = web.RouteTableDef()


@routes.get('/')
async def index(request):
    return web.HTTPPermanentRedirect('/user')


@routes.get('/user')
async def user(request):
    return web.Response(text='Hello, Anonymous!\nPlease login or sign up using your special key!')


@routes.get('/album')
async def album(request):
    return web.Response(text='I\'m working on this page')


@routes.get('/track')
async def album(request):
    return web.Response(text='I\'m working on this page')

app = web.Application()
app.add_routes(routes)
web.run_app(app)
