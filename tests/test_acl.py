import pytest

from client.api import API

PROJECT_NAME = "test_acl"


@pytest.fixture
def admin():
    api = API.login("admin", "admin")

    # Create a testing project

    response = api.put(
        f"/projects/{PROJECT_NAME}",
        folder_types={"AssetBuild": {}}
    )
    assert response.status == 201
    yield api

    # Try to delete project. It should return 404
    # as it should be already deleted by the manager
    response = api.delete(f"/projects/{PROJECT_NAME}")
    assert response.status == 404
    api.logout()


def test_project_delete(admin):
    # Try to delete the project as a normal user
    # It should return 403 (forbidden)

    api = API.login("user", "user")
    response = api.delete(f"/projects/{PROJECT_NAME}")
    assert response.status == 403

    # Now as a manager, who should be able to do that

    api = API.login("manager", "manager")
    response = api.delete(f"/projects/{PROJECT_NAME}")
    assert response.status == 204
