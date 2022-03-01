from client.api import API


def test_authentication():
    api = API.login("fake", "user")

    server_url = api.server_url

    response = api.get("users/me")
    assert response.status == 401

    response = api.gql("{me{name}}")
    assert not response

    api = API.login("admin", "admin")

    response = api.get("users/me")
    assert response.status == 200

    response = api.gql("{me{name}}")
    assert response
    assert response["me"]["name"] == "admin"

    api.logout()

    response = api.get("users/me")
    assert response.status == 401

    api = API(server_url, "fakeaccesstoken")

    response = api.get("users/me")
    assert response.status == 401
