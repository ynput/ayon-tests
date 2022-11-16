import pytest

from tests.fixtures import api, PROJECT_NAME
from client.api import API

USER_NAME = "test_artist"
PASSWORD = "123.456.AbCd"
ROLE_NAME1 = "test_artist_role1"
ROLE_NAME2 = "test_artist_role2"


def create_entity(api, entity_type: str, **kwargs):
    response = api.post(f"projects/{PROJECT_NAME}/{entity_type}s", **kwargs)
    assert response
    return response.data["id"]


@pytest.fixture
def admin(api):
    api.delete(f"/users/{USER_NAME}")

    yield api

    api.delete(f"/roles/{ROLE_NAME1}/_")
    api.delete(f"/users/{USER_NAME}")


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
    pr_id = create_entity(admin, "folder", name="props", parentId=as_id)

    ch_f = create_entity(admin, "folder", name="ch1", parentId=ch_id, attrib=attr)
    lo_f = create_entity(admin, "folder", name="lo1", parentId=lo_id)
    pr_f = create_entity(admin, "folder", name="pr1", parentId=pr_id)

    ch_s = create_entity(admin, "subset", name="chs", family="foo", folderId=ch_f)
    lo_s = create_entity(admin, "subset", name="chs", family="foo", folderId=lo_f)

    ch_t = create_entity(admin, "task", name="chs", taskType="Generic", folderId=ch_f)
    lo_t = create_entity(admin, "task", name="chs", taskType="Generic", folderId=lo_f)

    ch_v = create_entity(admin, "version", version=1, subsetId=ch_s)
    lo_v = create_entity(admin, "version", version=1, subsetId=lo_s)

    ch_r = create_entity(admin, "representation", name="psd", versionId=ch_v)
    lo_r = create_entity(admin, "representation", name="psd", versionId=lo_v)

    # Create a role with access to the assets/characters part of the project
    # And to the folders with tasks assigned to the user

    assert admin.put(
        f"/roles/{ROLE_NAME1}/_",
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
        attrib_read={
            "enabled": True,
            "attributes": ["resolutionWidth", "resolutionHeight"],
        },
    )

    assert admin.put(
        f"/roles/{ROLE_NAME2}/_",
        read={
            "enabled": True,
            "access_list": [
                {"access_type": "hierarchy", "path": "assets/props"},
                {"access_type": "assigned"},
            ],
        },
        update={
            "enabled": True,
            "access_list": [
                {"access_type": "assigned"},
            ],
        },
        attrib_read={
            "enabled": True,
            "attributes": ["fps"],
        },
    )

    # In the test environment, artist has access only to assets/characters
    # branch and to the folders with tasks assigned to them

    assert admin.put(f"/users/{USER_NAME}")
    assert admin.patch(f"/users/{USER_NAME}/password", password=PASSWORD)
    assert admin.patch(
        f"/users/{USER_NAME}/roles",
        roles=[{"roles": [ROLE_NAME1, ROLE_NAME2], "project": PROJECT_NAME}],
    )

    api = API.login(USER_NAME, PASSWORD)
    assert api.get("/users/me")

    response = api.get(f"/projects/{PROJECT_NAME}/folders/{ch_f}")
    assert response.status == 200
    # assert len(response.data["attrib"]) == 2
    assert "resolutionWidth" in response.data["attrib"]
    assert "resolutionHeight" in response.data["attrib"]

    # From role2, user should have read access to props
    response = api.get(f"/projects/{PROJECT_NAME}/folders/{pr_f}")
    assert response.status == 200

    # But not for writing unless a task is assigned
    response = api.patch(f"/projects/{PROJECT_NAME}/folders/{pr_f}", attrib={"fps": 99})
    assert response.status == 403

    # so... let's assing a task
    _ = create_entity(
        admin,
        "task",
        name="render",
        folderId=pr_f,
        taskType="Generic",
        assignees=[USER_NAME],
    )

    # and try again
    response = api.patch(f"/projects/{PROJECT_NAME}/folders/{pr_f}", attrib={"fps": 99})
    assert response.status == 204

    # To locations, user shouldn't have access at all
    response = api.get(f"/projects/{PROJECT_NAME}/folders/{lo_f}")
    assert response.status == 403

    # Test nested entities
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

    assert admin.put(f"/users/{USER_NAME}")
    assert admin.patch(f"/users/{USER_NAME}/password", password=PASSWORD)

    api = API.login(USER_NAME, PASSWORD)
    response = api.delete(f"/projects/{PROJECT_NAME}")
    assert response.status == 403

    # Now as a manager, who should be able to do that

    response = admin.delete(f"/projects/{PROJECT_NAME}")
    assert response.status == 204
