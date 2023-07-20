from tests.fixtures import api, PROJECT_NAME

assert api


def test_hierarchy(api):
    response = api.post(
        f"/projects/{PROJECT_NAME}/folders",
        folder_type="Asset",
        name="child1",
    )
    assert response
    child1 = response["id"]

    response = api.post(
        f"/projects/{PROJECT_NAME}/folders",
        folder_type="Asset",
        name="child2",
    )
    assert response
    child2 = response["id"]

    response = api.post(
        f"/projects/{PROJECT_NAME}/folders",
        folderType="Folder",
        name="parent",
    )
    assert response
    parent = response["id"]
