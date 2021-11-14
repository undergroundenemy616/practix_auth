import asyncio
from dataclasses import dataclass
from urllib.parse import urljoin

import pytest
import aiohttp
from sqlalchemy.future import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

from settings import Settings
from multidict import CIMultiDictProxy

config = Settings()
SERVICE_URL = f'http://{config.app_host}:{config.app_port}'

Base = declarative_base()


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
def db_engine():
    engine = create_engine(
        f'postgresql://{config.pg_user}:{config.pg_password}@{config.pg_host}/{config.pg_db}',
        echo=True
    )
    yield engine


@pytest.fixture(scope='session')
def db_session_factory(db_engine):
    return scoped_session(sessionmaker(bind=db_engine))


@pytest.fixture(scope='function')
def db_session(db_session_factory):
    session = db_session_factory()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def make_get_request(session):
    async def inner(method: str, headers: dict = None, params: dict = None) -> HTTPResponse:
        params = params or {}
        url = urljoin(SERVICE_URL, method)
        async with session.get(url, headers=headers, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner


@pytest.fixture
def make_post_request(session):
    async def inner(method: str, headers: dict = None, json_data: dict = None, params: dict = None) -> HTTPResponse:
        params = params or {}
        url = urljoin(SERVICE_URL, method)
        async with session.post(url, headers=headers, json=json_data, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )

    return inner
