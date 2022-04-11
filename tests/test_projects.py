from tests.fixtures import api, PROJECT_NAME

assert api


def test_projects(api):
    api.delete(f"/projects/{PROJECT_NAME}")

    response = api.put(
        f"/projects/{PROJECT_NAME}",
        name="this will be ignored",
        attrib={
            "fps": 25,
            "resolutionWidth": 1024,
            "resolutionHeight": 576,
        },
        data={"datakey": "dataval", "iwillstay": "here"},
        config={
            "cfgkey": "cfgval",
        },
    )
    assert response

    response = api.get("/projects/" + PROJECT_NAME)
    assert response

    assert response.data["name"] == PROJECT_NAME
    assert response.data["attrib"]["fps"] == 25
    assert response.data["config"].get("cfgkey") == "cfgval"
    assert response.data["data"].get("datakey") == "dataval"

    # Test project patch ing

    response = api.patch(
        f"/projects/{PROJECT_NAME}",
        attrib={"fps": 30},
        data={"datakey": None, "datakey2": "something"},
    )
    assert response

    response = api.get(f"/projects/{PROJECT_NAME}")
    assert response

    assert response.data["attrib"]["fps"] == 30
    assert response.data["attrib"]["resolutionWidth"] == 1024
    assert response.data["data"]["datakey2"] == "something"
    assert response.data["data"]["iwillstay"] == "here"
    assert "datakey" not in response["data"]
