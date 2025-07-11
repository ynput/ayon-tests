import time
import pytest
from tests.fixtures import api, PROJECT_NAME

assert api


@pytest.fixture
def folder_id(api):
    response = api.post(
        f"projects/{PROJECT_NAME}/folders",
        name="test",
        folderType="Asset",
    )
    assert response
    folder_id = response.data["id"]
    yield folder_id


def test_comment(api, folder_id):

    response = api.post(
        f"projects/{PROJECT_NAME}/operations/activities",
        operations=[
            {
                "type": "create",
                "data": {
                    "activityType": "comment",
                    "body": "test comment",
                    "entityType": "folder",
                    "entityId": folder_id,
                    "data" : {"mykey1": "myvalue1", "mykey2": "myvalue2"}
                }
            }
        ] 
    )

    assert response
    assert response.data["success"], f"response: {response.data}"
    activity_id = response.data["operations"][0]["activityId"]
    assert activity_id


    # patch the comment

    response = api.post(
        f"projects/{PROJECT_NAME}/operations/activities",
        operations=[
            {
                "type": "update",
                "activityId": activity_id,
                "data": {
                    "body": "test comment updated",
                    "data": {"mykey2": "updatedvalue2"}
                }
            }
        ] 
    )


    # patch using... patch 

    response = api.patch(
        f"projects/{PROJECT_NAME}/activities/{activity_id}",
        body="test comment updated again",
        data={"mykey2": "updatedvalue3"}
    )

    assert response


