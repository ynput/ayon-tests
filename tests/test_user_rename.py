import pytest
from tests.fixtures import api, PROJECT_NAME

ORIGINAL_USER_NAME = "novice"
NEW_USER_NAME = "expert"
OTHER_USER_NAME = "someoneelse"


@pytest.fixture()
def users(api):
    api.delete(f"/users/{ORIGINAL_USER_NAME}")
    api.delete(f"/users/{NEW_USER_NAME}")
    api.delete(f"/users/{OTHER_USER_NAME}")

    api.put(f"/users/{ORIGINAL_USER_NAME}")
    api.put(f"/users/{OTHER_USER_NAME}")

    yield

    api.delete(f"/users/{ORIGINAL_USER_NAME}")
    api.delete(f"/users/{NEW_USER_NAME}")
    api.delete(f"/users/{OTHER_USER_NAME}")


def test_user_rename(users, api):
    response = api.post(f"/projects/{PROJECT_NAME}/folders", name="assets")
    assert response
    root_folder_id = response.data["id"]
    response = api.post(
        f"/projects/{PROJECT_NAME}/folders",
        name="asset",
        folderType="Asset",
        parentId=root_folder_id,
    )
    assert response
    folder_id = response.data["id"]

    response = api.post(
        f"/projects/{PROJECT_NAME}/tasks",
        name="jit_se_smetim",
        taskType="Generic",
        folderId=folder_id,
        assignees=[ORIGINAL_USER_NAME, OTHER_USER_NAME],
    )
    assert response
    task_id = response.data["id"]

    response = api.patch(f"/users/{ORIGINAL_USER_NAME}/rename", newName=NEW_USER_NAME)
    assert response

    response = api.get(f"/users/{NEW_USER_NAME}")
    assert response

    response = api.get(f"/projects/{PROJECT_NAME}/tasks/{task_id}")

    assert response and response.data["assignees"]
    assignees = response.data["assignees"]
    assert len(assignees) == 2
    assert NEW_USER_NAME in assignees
    assert OTHER_USER_NAME in assignees
