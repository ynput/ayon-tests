import pytest
from client.api import API

PROJECT_NAME = "test_project"
PROJECT_META = {
    "code": "test",
    "folderTypes": [
        {"name": "Folder"},
        {"name": "Asset"},
    ],
    "taskTypes": [
        {"name": "Generic"},
    ],
    "statuses": [
        {"name": "Unknown"},
    ],
}


@pytest.fixture()
def api():
    api = API.login("admin", "admin")
    api.delete(f"/projects/{PROJECT_NAME}")
    assert api.put(f"/projects/{PROJECT_NAME}", **PROJECT_META)
    yield api
    api.delete(f"/projects/{PROJECT_NAME}")
    api.logout()
