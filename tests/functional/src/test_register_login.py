from http import HTTPStatus

import pytest

pytestmark = pytest.mark.asyncio


async def test_register(make_post_request, db_setup):
    login = "Test"
    password = "Testtest123"
    response = await make_post_request(f"/api/v1/accounts/register", json_data={"login": login, "password": password})

    assert response.status == HTTPStatus.CREATED
    assert response.body['message'] == "Пользователь Test успешно зарегистрирован"
    assert response.body['access_token']
    assert response.body['refresh_token']


async def test_not_register_existing_login(make_post_request, db_setup):
    login = "Testtest"
    password = "Testtest123"
    response = await make_post_request(f"/api/v1/accounts/register", json_data={"login": login, "password": password})

    assert response.status == HTTPStatus.BAD_REQUEST
    assert response.body['error'] == "Пользователь с таким login уже зарегистрирован"


async def test_not_register_wrong_password(make_post_request, db_setup):
    login = "Testtest"
    password = "123"
    response = await make_post_request(f"/api/v1/accounts/register", json_data={"login": login, "password": password})

    assert response.status == HTTPStatus.BAD_REQUEST
    assert response.body['password'] == [
        "Пароль должен иметь буквы в обоих регистрах, цифры и быть длиной не менее 8 символов."
    ]


async def test_register_login(make_post_request, db_setup):
    login = "Test"
    password = "Testtest123"
    await make_post_request(f"/api/v1/accounts/register", json_data={"login": login, "password": password})
    response = await make_post_request(f"/api/v1/accounts/login", json_data={"login": login, "password": password})

    assert response.status == HTTPStatus.OK
    assert response.body['access_token']
    assert response.body['refresh_token']


async def test_wrong_password_not_login(make_post_request, db_setup):
    login = "Testtest"
    password = "Testtest123"
    response = await make_post_request(f"/api/v1/accounts/login", json_data={"login": login, "password": password})

    assert response.status == HTTPStatus.FORBIDDEN
    assert response.body['error'] == "Неверная пара логин-пароль"
