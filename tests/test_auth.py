import pytest
from client.api import API

USERNAME = "testuser1"
PASSWORD = "jeuf8jfqf2fqj..FNDF"
APIKEY = "12340000000000000000000000004321"


@pytest.fixture()
def admin():
    api = API.login("admin", "admin")

    api.delete(f"/users/{USERNAME}")

    yield api

    api.delete(f"/users/{USERNAME}")
    api.logout()


def test_user_password(admin):

    response = admin.put(f"/users/{USERNAME}")
    assert response

    response = admin.patch(f"/users/{USERNAME}/password", password=PASSWORD)
    assert response

    try:
        usr = API.login(USERNAME, PASSWORD + "wrong")
    except Exception as e:
        usr = None

    assert not usr

    usr = API.login(USERNAME, PASSWORD)
    assert usr

    response = usr.get("/users/me")
    assert response
    assert response.data["name"] == USERNAME

    usr.logout()


    response = admin.patch(f"/users/{USERNAME}", data={"isService": True})
    assert response

    response = admin.patch(f"/users/{USERNAME}/password", apiKey=APIKEY)
    assert response 

    response = admin.get(f"/users/{USERNAME}")
    assert response
    assert response.data["data"].get("apiKey")
    assert response.data["data"].get("apiKeyPreview") == "1234***4321"


