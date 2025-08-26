from tests.fixtures import api, PROJECT_NAME

assert api


def test_uniqueness(api):
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
        name="Child1",
    )

    assert not response

    response = api.patch(
        f"/projects/{PROJECT_NAME}/folders/{child1}",
        name="Child1",
    )

    assert response

    response = api.patch(
        f"/projects/{PROJECT_NAME}/folders/{child1}",
        active=False,
    )

    assert response

    response = api.post(
        f"/projects/{PROJECT_NAME}/folders",
        folder_type="Asset",
        name="Child1",
    )

    assert response
