import time
import pytest
from tests.fixtures import api, PROJECT_NAME

assert api


def test_parent_change(api):

    response = api.post(
        f"projects/{PROJECT_NAME}/folders",
        name="root_folder",
        folderType="Folder",
    )

    assert response
    root_folder_id = response.data["id"]

    response = api.post(
        f"projects/{PROJECT_NAME}/folders",
        name="child_folder_1",
        folderType="Asset",
        parentId=root_folder_id,
    )

    assert response
    child_folder_1_id = response.data["id"]

    response = api.post(
        f"projects/{PROJECT_NAME}/folders",
        name="child_folder_2",
        folderType="Asset",
        parentId=child_folder_1_id,
    )
    assert response
    child_folder_2_id = response.data["id"]


    # moving root folder under child_folder_2 should fail
    response = api.patch(
        f"projects/{PROJECT_NAME}/folders/{root_folder_id}",
        parentId=child_folder_2_id,
    )
    assert not response

    # moving child_folder_1 under child_folder_2 should fail
    response = api.patch(
        f"projects/{PROJECT_NAME}/folders/{child_folder_1_id}",
        parentId=child_folder_2_id,
    )
    assert not response


    # moving child_folder_2 under root_folder should succeed
    response = api.patch(
        f"projects/{PROJECT_NAME}/folders/{child_folder_2_id}",
        parentId=root_folder_id,
    )
    assert response

