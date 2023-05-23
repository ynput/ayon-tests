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

    # response = api.post(
    #     f"/projects/{PROJECT_NAME}/hierarchy",
    #     id=parent,
    #     children=[child1, child2],
    # )
    # assert response
    #
    # response = api.get(f"/projects/{PROJECT_NAME}/folders/{child1}")
    # assert response
    # assert response.get("parentId") == parent
    #
    # response = api.get(f"/projects/{PROJECT_NAME}/folders/{child2}")
    # assert response
    # assert response.get("parentId") == parent
    #
    # response = api.post(
    #     f"/projects/{PROJECT_NAME}/hierarchy",
    #     id=None,
    #     children=[child1],
    # )
    # assert response
    #
    # response = api.get(f"/projects/{PROJECT_NAME}/folders/{child1}")
    # assert response
    # assert response.get("parentId") is None
    #
    # response = api.get(f"/projects/{PROJECT_NAME}/folders/{child2}")
    # assert response
    # assert response.get("parentId") == parent
