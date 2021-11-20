import json
from http import HTTPStatus

import pytest

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def get_token(db_setup, make_post_request):
    login = "Test"
    password = "paSSword1999"
    await make_post_request(f"/api/v1/accounts/register",
                            json_data={"login": login, "password": password})
    response = await make_post_request(f"/api/v1/accounts/login",
                                       json_data={"login": login, "password": password})
    return response.body['access_token']


async def test_retrieve_user(get_token, make_get_request):
    response = await make_get_request(f"/api/v1/accounts/account", headers={"Authorization": f"Bearer {get_token}"})

    assert response.status == HTTPStatus.OK
    assert json.loads(response.body['data']) == {"email": None, "login": "Test", "name": None}


async def test_update_user_login(get_token, make_post_request, make_get_request):
    new_login = "Test2"
    response = await make_post_request(f"/api/v1/accounts/account",
                                       json_data={"login": new_login},
                                       headers={"Authorization": f"Bearer {get_token}"})
    assert response.status == HTTPStatus.OK
    assert response.body["message"] == f"Пользователь Test успешно обновлен"

    response_after_login_change = await make_post_request(f"/api/v1/accounts/login",
                                                          json_data={"login": new_login, "password": "paSSword1999"})
    new_token = response_after_login_change.body['access_token']
    response = await make_get_request(f"/api/v1/accounts/account", headers={"Authorization": f"Bearer {new_token}"})

    assert response.status == HTTPStatus.OK
    assert json.loads(response.body['data']) == {"email": None, "login": "Test2", "name": None}


async def test_not_update_user_repeat_login(get_token, make_post_request, make_get_request):
    new_login = "Testtest"
    response = await make_post_request(f"/api/v1/accounts/account",
                                       json_data={"login": new_login},
                                       headers={"Authorization": f"Bearer {get_token}"})
    assert response.status == HTTPStatus.BAD_REQUEST
    assert response.body["message"] == "Пользователь с таким login уже зарегистрирован"
    assert response.body["status"] == "error"


async def test_update_user_password(get_token, make_post_request, make_get_request):
    new_password = "Testtest123"

    response = await make_post_request(f"/api/v1/accounts/account",
                                       json_data={"password": new_password},
                                       headers={"Authorization": f"Bearer {get_token}"})
    assert response.status == HTTPStatus.OK
    assert response.body["message"] == f"Пользователь Test успешно обновлен"

    response_after_password_change = await make_post_request(f"/api/v1/accounts/login",
                                                             json_data={"login": "Test", "password": new_password})
    new_token = response_after_password_change.body['access_token']
    response = await make_get_request(f"/api/v1/accounts/account", headers={"Authorization": f"Bearer {new_token}"})

    assert response.status == HTTPStatus.OK
    assert json.loads(response.body["data"]) == {"email": None, "login": "Test", "name": None}


async def test_not_update_user_incorrect_password(get_token, make_post_request, make_get_request):
    new_password = "Test1"
    response = await make_post_request(f"/api/v1/accounts/account",
                                       json_data={"password": new_password},
                                       headers={"Authorization": f"Bearer {get_token}"})
    assert response.status == HTTPStatus.BAD_REQUEST
    assert response.body["message"]["password"] == [
        "Пароль должен иметь буквы в обоих регистрах, цифры и быть длиной не менее 8 символов."
    ]


async def test_update_user_email(get_token, make_post_request, make_get_request):
    new_email = "Test@test.ru"
    response = await make_post_request(f"/api/v1/accounts/account",
                                       json_data={"email": new_email},
                                       headers={"Authorization": f"Bearer {get_token}"})
    assert response.status == HTTPStatus.OK
    assert response.body["message"] == f"Пользователь Test успешно обновлен"

    response = await make_get_request(f"/api/v1/accounts/account", headers={"Authorization": f"Bearer {get_token}"})

    assert response.status == HTTPStatus.OK
    assert json.loads(response.body["data"]) == {"email": new_email, "login": "Test", "name": None}


async def test_not_update_user_wrong_email(get_token, make_post_request, make_get_request):
    new_email = "Test"
    response = await make_post_request(f"/api/v1/accounts/account",
                                       json_data={"email": new_email},
                                       headers={"Authorization": f"Bearer {get_token}"})
    assert response.status == HTTPStatus.BAD_REQUEST
    assert response.body["message"]["email"] == ['Not a valid email address.']
