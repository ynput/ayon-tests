import time
import pytest

from tests.fixtures import api
from client.api import API

USER_NAME = "test_artist"
PASSWORD = "123.456.AbCd"
ROLE_NAME = "test_artist"
PROJECT_NAME = "test_new_project"


@pytest.fixture
def admin(api):
    api.delete(f"/users/{USER_NAME}")

    yield api

    api.delete(f"/accessGroups/{ROLE_NAME}/_")
    api.delete(f"/users/{USER_NAME}")
    api.delete(f"/projects/{PROJECT_NAME}")


@pytest.fixture
def access_group(admin):
    assert admin.put(
        f"/accessGroups/{ROLE_NAME}/_",
        create={
            "enabled": True,
            "access_list": [{"access_type": "hierarchy", "path": "assets/writable"}],
        },
        read={
            "enabled": True,
            "access_list": [
                {"access_type": "hierarchy", "path": "assets/characters"},
            ],
        },
        update={
            "enabled": True,
            "access_list": [
                {"access_type": "hierarchy", "path": "assets/characters"},
            ],
        },
        publish={"enabled": True, "access_list": [{"access_type": "assigned"}]},
        attrib_read={
            "enabled": True,
            "attributes": ["resolutionWidth", "resolutionHeight"],
        },
    )

    yield

    admin.delete(f"/accessGroups/{ROLE_NAME}/_")


@pytest.fixture
def artist(admin, access_group):
    assert admin.put(f"/users/{USER_NAME}", data={"defaultAccessGroups": [ROLE_NAME]})
    assert admin.patch(f"/users/{USER_NAME}/password", password=PASSWORD)

    artist = API.login(USER_NAME, PASSWORD)
    assert artist.get("/users/me")

    yield artist

    artist.logout()
    admin.delete(f"/users/{USER_NAME}")
    


def test_assigning(admin, artist):
    anatomy = admin.get("/anatomy/presets/_")
    assert admin.post(
        "/projects",
        name=PROJECT_NAME,
        code="xxxx",
        anatomy=anatomy.data,
    )

    assert artist.get(f"/projects/{PROJECT_NAME}")
