from tests.fixtures import api, PROJECT_NAME

assert api


def test_hierarchical_attrs(api):

    response = api.patch(
        f"projects/{PROJECT_NAME}",
        attrib={
            "resolutionWidth": 1920,
            "resolutionHeight": 1080,
        },
    )
    assert response

    response = api.post(
        f"projects/{PROJECT_NAME}/folders",
        name="testicek",
        folderType="Asset",
        attrib={"fps": 25},
    )
    assert response
    folder_id = response.data["id"]

    response = api.get(f"projects/{PROJECT_NAME}/folders/{folder_id}")
    assert response
    attrib = response.data["attrib"]

    assert attrib["fps"] == 25
    assert attrib["resolutionWidth"] == 1920

    # Create a child

    response = api.post(
        f"projects/{PROJECT_NAME}/folders",
        name="child",
        parentId=folder_id,
        folderType="Asset",
        attrib={"fps": 50},
    )
    assert response
    child_id = response.data["id"]

    # load the child

    response = api.get(f"projects/{PROJECT_NAME}/folders/{child_id}")
    assert response
    child_attrib = response.data["attrib"]

    assert child_attrib["fps"] == 50
    assert child_attrib["resolutionWidth"] == 1920
    assert child_attrib["resolutionHeight"] == 1080

    # Update the parent

    response = api.patch(
        f"projects/{PROJECT_NAME}/folders/{folder_id}", attrib={"resolutionWidth": 2000}
    )
    assert response

    # reload the child

    response = api.get(f"projects/{PROJECT_NAME}/folders/{child_id}")
    assert response
    assert response.data["ownAttrib"] == ["fps"]
    child_attrib = response.data["attrib"]

    assert child_attrib["fps"] == 50
    assert child_attrib["resolutionWidth"] == 2000
