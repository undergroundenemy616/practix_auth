from http import HTTPStatus

import pytest
from sqlalchemy import inspect, MetaData
from sqlalchemy.ext.automap import automap_base

from settings import Settings

pytestmark = pytest.mark.asyncio

config = Settings()


@pytest.fixture(scope='function')
async def register_setup(db_engine, db_session):
    metadata = MetaData(bind=db_engine)
    metadata.reflect(db_engine)
    Base = automap_base(metadata=metadata)
    Base.prepare()
    User = Base.classes.user
    test_user = User(id="5a8bad1b-586d-4283-a11c-af232bfd0005", login="Testtest", password="paSSword1999")
    db_session.add(test_user)
    db_session.commit()
    yield
    db_session.query(User).delete()
    db_session.commit()
    db_engine.dispose()


async def test_register(make_post_request, register_setup):
    login = "Test"
    password = "Testtest123"
    response = await make_post_request(f"/api/v1/accounts/register", json_data={"login": login, "password": password})

    assert response.status == HTTPStatus.CREATED
    assert response.body['message'] == "Пользователь Test успешно зарегистрирован"
    assert response.body['access_token']
    assert response.body['refresh_token']


async def test_not_register_existing_login(make_post_request, register_setup):
    login = "Testtest"
    password = "Testtest123"
    response = await make_post_request(f"/api/v1/accounts/register", json_data={"login": login, "password": password})

    assert response.status == HTTPStatus.BAD_REQUEST
    assert response.body['error'] == "Пользователь с таким login уже зарегистрирован"


async def test_not_register_wrong_password(make_post_request, register_setup):
    login = "Testtest"
    password = "123"
    response = await make_post_request(f"/api/v1/accounts/register", json_data={"login": login, "password": password})

    assert response.status == HTTPStatus.BAD_REQUEST
    assert response.body['password'] == [
        "Пароль должен иметь буквы в обоих регистрах, цифры и быть длиной не менее 8 символов."
    ]


