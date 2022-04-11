from tests.fixtures import api, PROJECT_NAME

assert api


def test_folders(api):
    response = api.post(
        f"projects/{PROJECT_NAME}/folders",
        name="testicek",
        folderType="Asset",
    )
    assert response

    folder_id = response.data["id"]

    # patching

    response = api.patch(
        f"projects/{PROJECT_NAME}/folders/{folder_id}", name="testicek2"
    )
    assert response


def test_unique_names(api):
    """One parent folder cannot have two children with the same name"""

    response = api.post(
        f"projects/{PROJECT_NAME}/folders",
        name="root",
        folderType="Asset",
    )
    assert response
    root_id = response["id"]

    response = api.post(
        f"projects/{PROJECT_NAME}/folders",
        name="test",
        folderType="Asset",
        parent_id=root_id,
    )
    assert response

    response = api.post(
        f"projects/{PROJECT_NAME}/folders",
        name="test",
        folderType="Asset",
        parent_id=root_id,
    )
    assert not response

    response = api.post(
        f"projects/{PROJECT_NAME}/folders",
        name="test",
        folderType="Asset",
        parent_id=root_id,
        active=False,
    )
    assert response

    response = api.post(
        f"projects/{PROJECT_NAME}/folders",
        name="root",
        folderType="Asset",
    )
    assert not response
