import asyncpg


async def create_db():
    conn = await asyncpg.connect('postgresql://mmapp@localhost/mmappdb', password='mmapp1234')
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS Users(
            id SERIAL PRIMARY KEY,
            name TEXT UNIQUE,
            pwd TEXT,
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


# from sqlalchemy import (
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
#     Column('users_id', Integer, ForeignKey('users.id', ondelete='SET NULL'))
# )
#
# tracks = Table(
#     'tracks', meta,
#
#     Column('id', Integer, primary_key=True),
#     Column('name', String(100), nullable=False),
#     Column('created_date', DateTime, nullable=False),
#     Column('albums_id', Integer, ForeignKey('albums.id', ondelete='CASCADE'))
# )
