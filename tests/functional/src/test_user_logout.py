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


async def test_revoke_user_token(get_token, make_delete_request, make_get_request):
    token = get_token
    response = await make_delete_request(f"/api/v1/accounts/logout", headers={"Authorization": f"Bearer {token}"})

    assert response.status == HTTPStatus.OK
    assert response.body['message'] == 'Сеанс пользователя Test успешно завершен'
    assert response.body['status'] == 'success'

    response_after_revoking = await make_get_request(f"/api/v1/accounts/update",
                                                     headers={"Authorization": f"Bearer {token}"})

    assert response_after_revoking.status == HTTPStatus.UNAUTHORIZED
    assert response_after_revoking.body == {
        "msg": "Token has been revoked"
    }
