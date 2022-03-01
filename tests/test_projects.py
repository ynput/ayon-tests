import pytest

from client.api import API


class TestProjects:
    @pytest.fixture(scope="class")
    def api(self):
        api = API.login("admin", "admin")
        self._delete_test_projects(api)
        yield api
        self._delete_test_projects(api)

    def _delete_test_projects(self, api):
        data = api.get("/projects?name=test_projects%").data
        for project in data["projects"]:
            api.delete("/projects/{}".format(project["name"]))

    def test_empty_project(self, api):
        response = api.put("/projects/test_projects_2")
        assert response

    def test_projects(self, api):
        project_name = "test_projects_1"

        response = api.put(
            f"/projects/{project_name}",
            name="this will be ignored",
            attrib={
                "fps": 25,
                "resolutionWidth": 1024,
                "resolutionHeight": 576,
            },
            data={
                "datakey": "dataval",
                "iwillstay": "here"
            },
            config={
                "cfgkey": "cfgval",
            }
        )
        assert response

        response = api.get("/projects/" + project_name)
        assert response

        assert response.data["name"] == project_name
        assert response.data["attrib"]["fps"] == 25
        assert response.data["config"].get("cfgkey") == "cfgval"
        assert response.data["data"].get("datakey") == "dataval"

        # Test project patch ing

        response = api.patch(
            f"/projects/{project_name}",
            attrib={"fps": 30},
            data={
                "datakey": None,
                "datakey2": "something"
            }
        )
        assert response

        response = api.get("/projects/" + project_name)
        assert response

        assert response.data["attrib"]["fps"] == 30
        assert response.data["attrib"]["resolutionWidth"] == 1024
        assert response.data["data"]["datakey2"] == "something"
        assert response.data["data"]["iwillstay"] == "here"
        assert "datakey" not in response["data"]
