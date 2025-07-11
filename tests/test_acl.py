import base64
import time
import pytest

from tests.fixtures import api, PROJECT_NAME
from client.api import API

USER_NAME = "test_artist"
PASSWORD = "123.456.AbCd"
ROLE_NAME1 = "test_artist_role1"
ROLE_NAME2 = "test_artist_role2"
ROLE_NAME3 = "test_artist_role3"


THUMBNAIL_DATA = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=")  # noqa

def create_entity(api, entity_type: str, **kwargs):
    response = api.post(f"projects/{PROJECT_NAME}/{entity_type}s", **kwargs)
    assert response
    return response.data["id"]


@pytest.fixture
def admin(api):
    api.delete(f"/users/{USER_NAME}")

    yield api

    api.delete(f"/accessGroups/{ROLE_NAME1}/_")
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
    writable_folder_id = create_entity(admin, "folder", name="writable", parentId=as_id)

    ch_f = create_entity(admin, "folder", name="ch1", parentId=ch_id, attrib=attr)
    lo_f = create_entity(admin, "folder", name="lo1", parentId=lo_id)
    pr_f = create_entity(admin, "folder", name="pr1", parentId=pr_id)

    ch_s = create_entity(admin, "product", name="chs", productType="foo", folderId=ch_f)
    lo_s = create_entity(admin, "product", name="chs", productType="foo", folderId=lo_f)

    ch_t = create_entity(admin, "task", name="chs", taskType="Generic", folderId=ch_f)
    lo_t = create_entity(admin, "task", name="chs", taskType="Generic", folderId=lo_f)

    ch_v = create_entity(admin, "version", version=1, productId=ch_s)
    lo_v = create_entity(admin, "version", version=1, productId=lo_s)

    ch_r = create_entity(admin, "representation", name="psd", versionId=ch_v)
    lo_r = create_entity(admin, "representation", name="psd", versionId=lo_v)

    # Create a role with access to the assets/characters part of the project
    # And to the folders with tasks assigned to the user

    assert admin.put(
        f"/accessGroups/{ROLE_NAME1}/_",
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

    assert admin.put(
        f"/accessGroups/{ROLE_NAME2}/_",
        create={"enabled": True},
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
        publish={"enabled": True, "access_list": [{"access_type": "assigned"}]},
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
        f"/users/{USER_NAME}/accessGroups",
        accessGroups=[
            {"accessGroups": [ROLE_NAME1, ROLE_NAME2], "project": PROJECT_NAME}
        ],
    )

    # resulting roleshet should have
    # - read access to assets/characters
    # - read access to assets/props
    # - read access to folders with assigned tasks
    # - update access to assets/characters
    # - update access to folders with assigned tasks
    # - ability to read fps, resolutionWidth and resolutionHeight attributes

    api = API.login(USER_NAME, PASSWORD)
    assert api.get("/users/me")

    # user should have read access to assets/characters because of the role1
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

    # so... let's assing a task on one of the folders in assets/props
    task_id = create_entity(
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
    assert api.get(f"/projects/{PROJECT_NAME}/products/{ch_s}")
    assert not api.get(f"/projects/{PROJECT_NAME}/products/{lo_s}")

    assert api.get(f"/projects/{PROJECT_NAME}/tasks/{ch_t}")
    assert not api.get(f"/projects/{PROJECT_NAME}/tasks/{lo_t}")

    assert api.get(f"/projects/{PROJECT_NAME}/versions/{ch_v}")
    assert not api.get(f"/projects/{PROJECT_NAME}/versions/{lo_v}")

    assert api.get(f"/projects/{PROJECT_NAME}/representations/{ch_r}")
    assert not api.get(f"/projects/{PROJECT_NAME}/representations/{lo_r}")

    # try to create a task as a normal user

    # this should fail as the user doesn't have access to the folder
    assert not api.post(
        f"/projects/{PROJECT_NAME}/tasks",
        name="test_task",
        folderId=ch_f,
        taskType="Generic",
    )

    # try:
    #     time.sleep(3600)
    # except KeyboardInterrupt:
    #     pass
    # but they do to assets/writable

    assert api.post(
        f"/projects/{PROJECT_NAME}/tasks",
        name="test_task",
        folderId=writable_folder_id,
        taskType="Generic",
        assignees=[USER_NAME],
    )

    # remove the user
    admin.delete("/users/test_artist")


def test_write_lock_folders_with_publishes(admin):
    f_id = create_entity(admin, "folder", name="foo")

    assert admin.patch(f"/projects/{PROJECT_NAME}/folders/{f_id}", name="bar")
    response = admin.get(f"/projects/{PROJECT_NAME}/folders/{f_id}")
    assert response
    assert response.data["name"] == "bar"

    # Now create a product and version

    s_id = create_entity(
        admin, "product", name="le_product", productType="complete", folderId=f_id
    )
    assert create_entity(admin, "version", version=1, productId=s_id)

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


def test_publishing(admin):
    # Create two folders, each with a task

    f1_id = create_entity(admin, "folder", name="assigned_folder")
    t1_id = create_entity(
        admin,
        "task",
        name="assigned_task",
        folderId=f1_id,
        taskType="Generic",
    )

    f2_id = create_entity(admin, "folder", name="unassigned_folder")
    t2_id = create_entity(
        admin,
        "task",
        name="unassigned_task",
        folderId=f2_id,
        taskType="Generic",
    )

    # Create a role.
    # This role is allowed to see everything, but users cannot modify
    # anything and they can only publish to the task assigned to them
    assert admin.put(
        f"/accessGroups/{ROLE_NAME3}/_",
        read={"enabled": True, "access_list": [{"access_type": "assigned"}]},
        create={"enabled": True},
        delete={"enabled": True},
        update={"enabled": True},
        publish={"enabled": True, "access_list": [{"access_type": "assigned"}]},
    )

    # Create a user and assign the role to him

    assert admin.put(f"/users/{USER_NAME}")
    assert admin.patch(f"/users/{USER_NAME}/password", password=PASSWORD)
    assert admin.patch(
        f"/users/{USER_NAME}/accessGroups",
        accessGroups=[{"accessGroups": [ROLE_NAME3], "project": PROJECT_NAME}],
    )

    # assign task 1 to the user

    assert admin.patch(f"/projects/{PROJECT_NAME}/tasks/{t1_id}", assignees=[USER_NAME])

    # Login as the user

    api = API.login(USER_NAME, PASSWORD)

    assert api.get(f"/projects/{PROJECT_NAME}/folders/{f1_id}")
    assert api.get(f"/projects/{PROJECT_NAME}/tasks/{t1_id}")

    assert not api.get(f"/projects/{PROJECT_NAME}/folders/{f2_id}")
    assert not api.get(f"/projects/{PROJECT_NAME}/tasks/{t2_id}")

    # Try to publish to the folder with task 1
    # (create a product and a version)

    s_id = create_entity(
        api, "product", name="le_product", productType="beer", folderId=f1_id
    )

    v1_id = create_entity(api, "version", version=1, productId=s_id)
    create_entity(api, "representation", name="ma", versionId=v1_id)

    # It should work

    # Try to publish to the folder with task 2

    assert not api.post(
        f"/projects/{PROJECT_NAME}/products",
        folderId=f2_id,
        productType="beer",
        name="le_beer",
    )

    # now create the same as admin

    p2_id = create_entity(
        admin, "product", name="le_product", productType="beer", folderId=f2_id
    )

    # and ensure version cannot be created by user

    assert not api.post(
        f"/projects/{PROJECT_NAME}/versions",
        productId=p2_id,
        version=1,
    )

    # try create workfile for task 1
    # it should work

    assert api.post(
        f"/projects/{PROJECT_NAME}/workfiles",
        taskId=t1_id,
        path="/some/path",
        name="wfname",
    )

    # try create workfile for task 2
    # it should fail

    assert not api.post(
        f"/projects/{PROJECT_NAME}/workfiles",
        taskId=t2_id,
        path="/some/other/path",
        name="wfname2",
    )

    # as long user has access to the task, he can assign thumbnails
    # to folders even if he doesn't have update access to the folder

    assert api.raw_post(
        f"projects/{PROJECT_NAME}/folders/{f1_id}/thumbnail",
        mime="image/png",
        data=THUMBNAIL_DATA,
    )

    assert not api.raw_post(
        f"projects/{PROJECT_NAME}/folders/{f2_id}/thumbnail",
        mime="image/png",
        data=THUMBNAIL_DATA,
    )

    # they should even create a blind thumbnail

    response = api.raw_post(
        f"projects/{PROJECT_NAME}/thumbnails",
        mime="image/png",
        data=THUMBNAIL_DATA,
    )
    assert response

    thumb_id = response.data["id"]

    # and assign it to the folder

    assert api.patch(f"projects/{PROJECT_NAME}/folders/{f1_id}", thumbnailId=thumb_id)

    # but not to the other folder

    assert not api.patch(
        f"projects/{PROJECT_NAME}/folders/{f2_id}", thumbnailId=thumb_id
    )

    api.delete(f"/accessGroups/{ROLE_NAME3}/_")
    api.delete(f"/users/{USER_NAME}")


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
