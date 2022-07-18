import pytest

from client.api import API

PROJECT_NAME = "test_acl"
USER_NAME = "test_artist"
PASSWORD = "123.456.AbCd"
ROLE_NAME = "test_artist_role"


def create_entity(api, entity_type: str, **kwargs):
    response = api.post(f"projects/{PROJECT_NAME}/{entity_type}s", **kwargs)
    assert response
    return response.data["id"]


@pytest.fixture
def admin():
    api = API.login("admin", "admin")

    api.delete(f"/users/{USER_NAME}")
    api.delete(f"/projects/{PROJECT_NAME}")

    # Create a testing project

    response = api.put(
        f"/projects/{PROJECT_NAME}",
        code="test",
        folder_types={"AssetBuild": {}},
        task_types={"foo": {}},
    )
    assert response.status == 201

    yield api

    # Try to delete project. It should return 404
    # as it should be already deleted by the manager
    api.delete(f"/projects/{PROJECT_NAME}")
    api.delete(f"/roles/{ROLE_NAME}/_")
    api.delete(f"/users/{USER_NAME}")
    api.logout()


def test_folder_access(admin):

    attr = {
        "resolutionWidth": 1920,
        "resolutionHeight": 1080,
        "fps": 25,
        "whatever": "nope",
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

    # Create a role with access to the assets/characters part of the project
    # And to the folders with tasks assigned to the user

    assert admin.put(
        f"/roles/{ROLE_NAME}/_",
        read=[
            {
                "access_type": "hierarchy",
                "path": "assets/characters",
            },
            {
                "access_type": "assigned",
            },
        ],
        update=[
            {
                "access_type": "hierarchy",
                "path": "assets/characters",
            },
            {
                "access_type": "assigned",
            },
        ],
        attrib_read=["resolutionWidth", "resolutionHeight"],
    )

    # In the test environment, artist has access only to assets/characters
    # branch and to the folders with tasks assigned to them

    assert admin.put(f"/users/{USER_NAME}")
    assert admin.patch(f"/users/{USER_NAME}/password", password=PASSWORD)
    assert admin.patch(
        f"/users/{USER_NAME}/roles",
        roles=[{"role": ROLE_NAME, "projects": [PROJECT_NAME]}],
    )

    api = API.login(USER_NAME, PASSWORD)
    assert api.get("/users/me")

    response = api.get(f"/projects/{PROJECT_NAME}/folders/{ch_f}")
    assert response.status == 200
    # assert len(response.data["attrib"]) == 2
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

    admin.delete("/users/test_artist")


def test_write_lock_folders_with_publishes(admin):
    f_id = create_entity(admin, "folder", name="foo")

    assert admin.patch(f"/projects/{PROJECT_NAME}/folders/{f_id}", name="bar")
    response = admin.get(f"/projects/{PROJECT_NAME}/folders/{f_id}")
    assert response
    assert response.data["name"] == "bar"

    # Now create a subset and version

    s_id = create_entity(
        admin, "subset", name="le_subset", family="complete", folderId=f_id
    )
    assert create_entity(admin, "version", version=1, subsetId=s_id)

    # it shouldn't be possible to change the name of the folder now
    assert not admin.patch(f"/projects/{PROJECT_NAME}/folders/{f_id}", name="no_way")

    # but you can change attributes
    assert admin.patch(
        f"/projects/{PROJECT_NAME}/folders/{f_id}", attrib={"resolutionWidth": 42}
    )

    response = admin.get(f"/projects/{PROJECT_NAME}/folders/{f_id}")
    assert response
    assert response.data["name"] == "bar"
    assert response.data["attrib"]["resolutionWidth"] == 42


@pytest.mark.order(-1)
def test_project_delete(admin):
    # Try to delete the project as a normal user
    # It should return 403 (forbidden)

    api = API.login("user", "user")
    response = api.delete(f"/projects/{PROJECT_NAME}")
    assert response.status == 403

    # Now as a manager, who should be able to do that

    response = admin.delete(f"/projects/{PROJECT_NAME}")
    assert response.status == 204
