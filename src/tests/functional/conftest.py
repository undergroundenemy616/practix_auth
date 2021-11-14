import asyncio
from asyncio import current_task
from dataclasses import dataclass
from urllib.parse import urljoin

import pytest
import aiohttp
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine, async_scoped_session, AsyncSession
from sqlalchemy.future import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

from app import create_app
from db.pg_db import db
from models import User
from settings import TestSettings
from multidict import CIMultiDictProxy

config = TestSettings()
SERVICE_URL = f'http://{config.app_host}:{config.app_port}'

Base = declarative_base()


@pytest.fixture(scope='module')
def test_client():
    app = create_app('core.config.TestBaseConfig')
    client = app.test_client()
    context = app.app_context()
    context.push()

    yield client

    context.pop()


@pytest.fixture(scope='module')
def init_database():
    # Create the database and the database table
    db.create_all()

    # Insert user data
    user1 = User(email='patkennedy79@gmail.com', plaintext_password='FlaskIsAwesome')
    user2 = User(email='kennedyfamilyrecipes@gmail.com', plaintext_password='PaSsWoRd')
    db.session.add(user1)
    db.session.add(user2)

    # Commit the changes for the users
    db.session.commit()

    yield db  # this is where the testing happens!

    db.drop_all()

# @pytest.fixture(scope='session')
# async def session():
#     session = aiohttp.ClientSession()
#     yield session
#     await session.close()
#
#
# @pytest.fixture
# def make_get_request(session):
#     async def inner(method: str, headers: dict = None, params: dict = None) -> HTTPResponse:
#         params = params or {}
#         url = urljoin(SERVICE_URL, method)
#         async with session.get(url, headers=headers, params=params) as response:
#             return HTTPResponse(
#                 body=await response.json(),
#                 headers=response.headers,
#                 status=response.status,
#             )
#
#     return inner
#
#
# @pytest.fixture
# def make_post_request(session):
#     async def inner(method: str, headers: dict = None, json_data: dict = None, params: dict = None) -> HTTPResponse:
#         params = params or {}
#         url = urljoin(SERVICE_URL, method)
#         async with session.post(url, headers=headers, json=json_data, params=params) as response:
#             return HTTPResponse(
#                 body=await response.json(),
#                 headers=response.headers,
#                 status=response.status,
#             )
#
#     return inner
