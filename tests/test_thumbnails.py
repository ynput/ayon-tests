import base64

from tests.fixtures import api, PROJECT_NAME

assert api


thumb1 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="  # noqa
thumb2 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAA1JREFUGFdj+L+U4T8ABu8CpCYJ1DQAAAAASUVORK5CYII="  # noqa


THUMB_DATA1 = base64.b64decode(thumb1)
THUMB_DATA2 = base64.b64decode(thumb2)


def test_folder_thumbnail(api):
    response = api.post(
        f"projects/{PROJECT_NAME}/folders",
        name="testicek",
        folderType="Asset",
    )
    assert response
    folder_id = response.data["id"]

    # Ensure we cannot create an empty thumbnail

    assert not api.raw_post(
        f"projects/{PROJECT_NAME}/folders/{folder_id}/thumbnail",
        mime="image/png",
        data=b"",
    )

    # Create a thumbnail for the folder

    response = api.raw_post(
        f"projects/{PROJECT_NAME}/folders/{folder_id}/thumbnail",
        mime="image/png",
        data=THUMB_DATA1,
    )
    assert response

    # Ensure the thumbnail is there

    response = api.raw_get(f"projects/{PROJECT_NAME}/folders/{folder_id}/thumbnail")
    assert response == THUMB_DATA1

    # Get the id of the thumbnail (we can re-use it later)

    thumb1_id = api.get(
        f"projects/{PROJECT_NAME}/folders/{folder_id}",
    ).data["thumbnailId"]

    # Update thumbnail

    response = api.raw_post(
        f"projects/{PROJECT_NAME}/folders/{folder_id}/thumbnail",
        mime="image/png",
        data=THUMB_DATA2,
    )
    assert response

    # Ensure the thumbnail changed

    response = api.raw_get(f"projects/{PROJECT_NAME}/folders/{folder_id}/thumbnail")
    assert response == THUMB_DATA2

    # Let the folder use the old thumbnail

    response = api.patch(
        f"projects/{PROJECT_NAME}/folders/{folder_id}",
        thumbnail_id=thumb1_id,
    )
    assert response

    # Ensure the thumbnail is switched to the old one

    response = api.raw_get(f"projects/{PROJECT_NAME}/folders/{folder_id}/thumbnail")
    assert response == THUMB_DATA1


def test_version_thumbnail(api):

    # Create folder/product/version

    response = api.post(
        f"projects/{PROJECT_NAME}/folders",
        name="test2",
        folderType="Asset",
    )
    assert response

    folder_id = response.data["id"]

    response = api.post(
        f"projects/{PROJECT_NAME}/products",
        name="test2s",
        productType="theSopranos",
        folderId=folder_id,
    )
    assert response

    product_id = response.data["id"]

    response = api.post(
        f"projects/{PROJECT_NAME}/versions",
        version=1,
        productId=product_id,
    )

    version_id = response.data["id"]

    # Create thumbnail for the version

    response = api.raw_post(
        f"projects/{PROJECT_NAME}/versions/{version_id}/thumbnail",
        mime="image/png",
        data=THUMB_DATA1,
    )
    assert response

    # Verify that the thumbnail is there

    response = api.raw_get(f"projects/{PROJECT_NAME}/versions/{version_id}/thumbnail")
    assert response == THUMB_DATA1

def test_task_thumbnail(api):
    # Create a thumb first

    response = api.post(
        f"projects/{PROJECT_NAME}/folders",
        name="workfile_parent",
        folderType="Asset",
    )
    assert response
    folder_id = response.data["id"]

    # Create a task on the folder

    response = api.post(
        f"projects/{PROJECT_NAME}/tasks",
        name="workfile_task",
        taskType="Generic",
        folderId=folder_id,
    )

    assert response
    task_id = response.data["id"]

    # Create a thumbnail for the workfile

    response = api.raw_post(
        f"projects/{PROJECT_NAME}/tasks/{task_id}/thumbnail",
        mime="image/png",
        data=THUMB_DATA1,
    )
    assert response

    # Ensure the thumbnail is there

    response = api.raw_get(f"projects/{PROJECT_NAME}/tasks/{task_id}/thumbnail")
    assert response == THUMB_DATA1

def test_workfile_thumbnail(api):
    # Create a folder first

    response = api.post(
        f"projects/{PROJECT_NAME}/folders",
        name="workfile_parent",
        folderType="Asset",
    )
    assert response
    folder_id = response.data["id"]

    # Create a task on the folder

    response = api.post(
        f"projects/{PROJECT_NAME}/tasks",
        name="workfile_task",
        taskType="Generic",
        folderId=folder_id,
    )

    assert response
    task_id = response.data["id"]

    # Create a workfile

    response = api.post(
        f"projects/{PROJECT_NAME}/workfiles",
        name="test_workfile",
        path="/some/path",
        taskId=task_id,
    )
    assert response
    workfile_id = response.data["id"]

    # Create a thumbnail for the workfile

    response = api.raw_post(
        f"projects/{PROJECT_NAME}/workfiles/{workfile_id}/thumbnail",
        mime="image/png",
        data=THUMB_DATA1,
    )
    assert response

    # Ensure the thumbnail is there

    response = api.raw_get(f"projects/{PROJECT_NAME}/workfiles/{workfile_id}/thumbnail")
    assert response == THUMB_DATA1


def test_direct_thumbnail(api):
    # Create a thumbnail not associated with any entity

    response = api.raw_post(
        f"projects/{PROJECT_NAME}/thumbnails",
        mime="image/png",
        data=THUMB_DATA1,
    )
    assert response

    thumb_id = response.data["id"]

    # Create a folder and associate the thumbnail with it

    response = api.post(
        f"projects/{PROJECT_NAME}/folders",
        name="test3",
        folderType="Asset",
        thumbnail_id=thumb_id,
    )
    assert response

    folder_id = response.data["id"]

    # Ensure the thumbnail is there

    response = api.raw_get(f"projects/{PROJECT_NAME}/folders/{folder_id}/thumbnail")
    assert response == THUMB_DATA1
