import asyncpg
import hashlib
import uuid


salt = '3D4M'


async def create_db():
    conn = await asyncpg.connect('postgresql://mmapp@localhost/mmappdb', password='mmapp1234')
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS Users(
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            pwd TEXT NOT NULL,
            email TEXT,
            age INTEGER,
            location TEXT,
            api_key UUID UNIQUE NOT NULL,
            created_date TIMESTAMP NOT NULL,
            active_status BOOL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Albums(
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            created_date TIMESTAMP NOT NULL,
            user_id INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Tracks(
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            created_date TIMESTAMP NOT NULL,
            album_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL
        );
    ''')
    await conn.close()


async def user_signup(conn, new_user, clear_pwd, date_time, active_status):
    pwd = hashlib.sha256((clear_pwd + salt).encode()).hexdigest()
    row = await conn.execute('INSERT INTO Users'
                             '(name, pwd, api_key, created_date, active_status)'
                             'VALUES ($1,$2,$3,$4,$5)'
                             'ON CONFLICT (name) DO NOTHING',
                             new_user, pwd, uuid.uuid4(), date_time, active_status)
    result = [0]
    if int(row.split()[2]) > 0:
        result = await conn.fetchrow('SELECT api_key FROM Users WHERE name=$1', new_user)
    return result[0]


async def user_login(conn, username, clear_pwd):
    pwd = hashlib.sha256((clear_pwd + salt).encode()).hexdigest()
    result = await conn.fetchrow('SELECT api_key FROM Users WHERE name=$1 AND pwd=$2', username, pwd)
    return result[0]


async def get_user_by_api_key(request, api_key):
    async with request.app['db'].acquire() as conn:
        row = await conn.fetchrow('SELECT id, name, email, age, location FROM Users WHERE api_key=$1', api_key)
        return row


async def get_user_by_name(request, name):
    async with request.app['db'].acquire() as conn:
        row = await conn.fetchrow('SELECT id, api_key, location FROM Users WHERE name=$1', name)
        return row


async def update_user_info(request, info, api_key):
    if 'pwd' in info:
        info['pwd'] = hashlib.sha256((info['pwd'] + salt).encode()).hexdigest()
    async with request.app['db'].acquire() as conn:
        row = ''
        for k, v in info.items():
            row += await conn.execute('UPDATE Users SET name=$1 WHERE api_key=$2', v, api_key)
        return row


async def get_user_albums_by_api_key(request, api_key):
    async with request.app['db'].acquire() as conn:
        row = await conn.fetchrow('SELECT id, title FROM Albums WHERE user_id=$1', api_key)
        return row


async def get_user_tracks_by_api_key(request, api_key):
    async with request.app['db'].acquire() as conn:
        row = await conn.fetchrow('SELECT id, title FROM Tracks WHERE user_id=$1', api_key)
        return row




# from sqlalchemy import (get_user_tracks_by_api_key
#     MetaData, Table, Column, ForeignKey,
#     Integer, String, DateTime, Boolean
# )
# from sqlalchemy.dialects.postgresql import UUID
#
#
# meta = MetaData()
#
# users = Table(
#     'users', meta,
#
#     Column('id', Integer, primary_key=True),
#     Column('name', String(50), nullable=False, unique=True),
#     Column('password', String(200), nullable=False),
#     Column('email', String(100)),
#     Column('location', String(50)),
#     Column('api_key', UUID, nullable=False),
#     Column('created_date', DateTime, nullable=False),
#     Column('active_status', Boolean, nullable=False)
# )
#
# albums = Table(
#     'albums', meta,
#
#     Column('id', Integer, primary_key=True),
#     Column('name', String(100), nullable=False),
#     Column('created_date', DateTime, nullable=False),
#     Column('user_id', Integer, ForeignKey('users.id', ondelete='SET NULL'))
# )
#
# tracks = Table(
#     'tracks', meta,
#
#     Column('id', Integer, primary_key=True),
#     Column('name', String(100), nullable=False),
#     Column('created_date', DateTime, nullable=False),
#     Column('album_id', Integer, ForeignKey('albums.id', ondelete='CASCADE'))
#     Column('user_id', Integer, ForeignKey('albums.id', ondelete='CASCADE'))
# )
