from pathlib import Path
from aiohttp import web

# from .middlewares import check_api_key
# from .views import User, SignUp, Index

# def setup_routes(app):
#     app.add_routes([
#         web.get('/', Index, name='index', expect_handler=check_api_key),
#         web.get('/signup', SignUp, name='signup', expect_handler=check_api_key),
#         web.get('/user', User, name='user', expect_handler=check_api_key),
#     ])
    # app.router.add_route('GET', '/', Index, name='index')
    # app.router.add_route('GET', '/signup', SignUp, name='signup')
    # app.router.add_route('GET', '/user', User, name='user', expect_handler=check_api_key)
    # app.router.add_post('/login', login, name='login')
    # app.router.add_get('/logout', logout, name='logout')
    # app.router.add_get('/create', create_post, name='create-post')
    # app.router.add_post('/create', create_post, name='create-post')


PROJECT_ROOT = Path(__file__).parent


def setup_static_routes(app):
    app.router.add_static('/static/',
                          PROJECT_ROOT / 'static',
                          name='static')
