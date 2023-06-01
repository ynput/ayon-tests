import sys
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
        f"projects/{PROJECT_NAME}/folders/{folder_id}",
        attrib={"resolutionWidth": 2000},
    )
    assert response

    # check the parent

    response = api.get(f"projects/{PROJECT_NAME}/folders/{folder_id}")
    assert response
    attrib = response.data["attrib"]
    assert attrib["resolutionWidth"] == 2000

    # reload the child

    response = api.get(f"projects/{PROJECT_NAME}/folders/{child_id}")
    assert response
    assert response.data["ownAttrib"] == ["fps"]
    child_attrib = response.data["attrib"]

    assert child_attrib["fps"] == 50
    assert child_attrib["resolutionWidth"] == 2000

    # check using graphql

    query = f"""
    query {{
        project(name: "{PROJECT_NAME}") {{
            folder(id: "{child_id}") {{
                ownAttrib
                attrib {{
                    fps
                    resolutionWidth
                    resolutionHeight
                }}
            }}
        }}
    }}
    """

    response = api.gql(query)

    assert response
    assert response.data["project"]["folder"]["attrib"]["fps"] == 50
    assert response.data["project"]["folder"]["ownAttrib"] == ["fps"]

    # create a child task

    response = api.post(
        f"projects/{PROJECT_NAME}/tasks",
        name="a_task",
        folderId=child_id,
        taskType="Generic",
        attrib={"resolutionHeight": 1234},
    )

    assert response
    task_id = response.data["id"]

    # load the task

    response = api.get(f"projects/{PROJECT_NAME}/tasks/{task_id}")
    assert response

    assert response.data["ownAttrib"] == ["resolutionHeight"]
    assert response.data["attrib"]["resolutionHeight"] == 1234
    assert response.data["attrib"]["resolutionWidth"] == 2000
    assert response.data["attrib"]["fps"] == 50

    # patch using operations endpoint

    operations = [
        {
            "type": "update",
            "entityType": "task",
            "entityId": task_id,
            "data": {"attrib": {"fps": 65}},
        },
    ]

    response = api.post(
        f"/projects/{PROJECT_NAME}/operations",
        operations=operations,
        canFail=False,
    )

    assert response

    response = api.get(f"projects/{PROJECT_NAME}/tasks/{task_id}")

    assert response
    assert len(response.data["ownAttrib"]) == 2
    assert "fps" in response.data["ownAttrib"]
    assert "resolutionHeight" in response.data["ownAttrib"]
    assert response.data["attrib"]["resolutionHeight"] == 1234
    assert response.data["attrib"]["resolutionWidth"] == 2000
    assert response.data["attrib"]["fps"] == 65

    # set fps back to inherited (None)

    operations = [
        {
            "type": "update",
            "entityType": "task",
            "entityId": task_id,
            "data": {"attrib": {"fps": None}},
        },
    ]

    response = api.post(
        f"/projects/{PROJECT_NAME}/operations",
        operations=operations,
        canFail=False,
    )

    # try:
    #     import time
    #     time.sleep(3500)
    # except KeyboardInterrupt:
    #     pass

    query = f"""
    query ReCheck {{
        project(name: "{PROJECT_NAME}") {{
            task(id: "{task_id}") {{
                ownAttrib 
                attrib {{
                    fps
                    resolutionHeight
                    resolutionWidth
                }}
            }}
        }}
    }}
    """

    # try loading and checking using graphql too

    response = api.gql(query)
    assert response
    assert response.data["project"]["task"]["ownAttrib"] == ["resolutionHeight"]
    assert response.data["project"]["task"]["attrib"]["resolutionHeight"] == 1234
    assert response.data["project"]["task"]["attrib"]["fps"] == 50
