import json
from http import HTTPStatus

import pytest


pytestmark = pytest.mark.asyncio


async def test_register(make_post_request):
    login = "Test"
    password = "Testtest123"
    response = await make_post_request(f"/api/v1/accounts/register", json_data={"login": login, "password": password})

    assert response.status == HTTPStatus.CREATED
    assert response.body['message'] == "Пользователь Test успешно зарегистрирован"
    assert response.body['access_token']
    assert response.body['refresh_token']
    # assert response.body['rating'] == test_data_film['rating']
    # assert response.body['title'] == test_data_film['title']


def test_valid_login_logout(test_client, init_database):
    """
    GIVEN a Flask application
    WHEN the '/login' page is posted to (POST)
    THEN check the response is valid
    """
    response = test_client.post('/login',
                                data=dict(email='patkennedy79@gmail.com', password='FlaskIsAwesome'),
                                follow_redirects=True)
    assert response.status_code == 200
    assert b"Thanks for logging in, patkennedy79@gmail.com!" in response.data
    assert b"Welcome patkennedy79@gmail.com!" in response.data
    assert b"Flask User Management" in response.data
    assert b"Logout" in response.data
    assert b"Login" not in response.data
    assert b"Register" not in response.data

    """
    GIVEN a Flask application
    WHEN the '/logout' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Goodbye!" in response.data
    assert b"Flask User Management" in response.data
    assert b"Logout" not in response.data
    assert b"Login" in response.data
    assert b"Register" in response.dataугу