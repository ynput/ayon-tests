import pytest

from client.api import API

PROJECT_NAME = "test_acl"


def create_entity(api, entity_type: str, **kwargs):
    response = api.post(
        f"projects/{PROJECT_NAME}/{entity_type}s",
        **kwargs
    )
    assert response
    return response.data["id"]


@pytest.fixture
def admin():
    api = API.login("admin", "admin")

    # Create a testing project

    response = api.put(
        f"/projects/{PROJECT_NAME}",
        folder_types={"AssetBuild": {}},
        task_types={"foo": {}}
    )
    assert response.status == 201
    yield api

    # Try to delete project. It should return 404
    # as it should be already deleted by the manager
    response = api.delete(f"/projects/{PROJECT_NAME}")
    api.logout()


def test_folder_access(admin):

    attr = {
        "resolutionWidth": 1920,
        "resolutionHeight": 1080,
        "fps": 25,
        "whatever": "nope"
    }

    as_id = create_entity(admin, "folder", name="assets")
    ch_id = create_entity(admin, "folder", name="characters", parentId=as_id)
    lo_id = create_entity(admin, "folder", name="locations", parentId=as_id)

    ch_f = create_entity(admin, "folder", name="ch1", parentId=ch_id, attrib=attr)
    lo_f = create_entity(admin, "folder", name="lo1", parentId=lo_id)

    ch_s = create_entity(admin, "subset", name="chs", family="foo", folderId=ch_f)
    lo_s = create_entity(admin, "subset", name="chs", family="foo", folderId=lo_f)

    ch_t = create_entity(admin, "task", name="chs", taskType="foo", folderId=ch_f)
    lo_t = create_entity(admin, "task", name="chs", taskType="foo", folderId=lo_f)

    ch_v = create_entity(admin, "version", version=1, subsetId=ch_s)
    lo_v = create_entity(admin, "version", version=1, subsetId=lo_s)

    ch_r = create_entity(admin, "representation", name="psd", versionId=ch_v)
    lo_r = create_entity(admin, "representation", name="psd", versionId=lo_v)

    # In the test environment, artist has access only to assets/characters
    # branch and to the folders with tasks assigned to them
    api = API.login("artist", "artist")

    response = api.get(f"/projects/{PROJECT_NAME}/folders/{ch_f}")
    assert response.status == 200
    assert len(response.data["attrib"]) == 2
    assert "resolutionWidth" in response.data["attrib"]
    assert "resolutionHeight" in response.data["attrib"]

    response = api.get(f"/projects/{PROJECT_NAME}/folders/{lo_f}")
    assert response.status == 403

    assert api.get(f"/projects/{PROJECT_NAME}/subsets/{ch_s}")
    assert not api.get(f"/projects/{PROJECT_NAME}/subsets/{lo_s}")

    assert api.get(f"/projects/{PROJECT_NAME}/tasks/{ch_t}")
    assert not api.get(f"/projects/{PROJECT_NAME}/tasks/{lo_t}")

    assert api.get(f"/projects/{PROJECT_NAME}/versions/{ch_v}")
    assert not api.get(f"/projects/{PROJECT_NAME}/versions/{lo_v}")

    assert api.get(f"/projects/{PROJECT_NAME}/representations/{ch_r}")
    assert not api.get(f"/projects/{PROJECT_NAME}/representations/{lo_r}")


@pytest.mark.order(-1)
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
