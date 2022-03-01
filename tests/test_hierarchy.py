import pytest

from client.api import API


class Folders:
    project_name = "test_hierarchy"

    @pytest.fixture(scope="class")
    def api(self):
        api = API.login("admin", "admin")

        response = api.put(
            f"/projects/{self.project_name}",
            folder_types={"AssetBuild": {}}
        )
        assert response.status == 201

        yield api

        response = api.delete(f"/projects/{self.project_name}")
        assert response.status == 204
        api.logout()

    def test_hierarchy(self, api):
        response = api.post(
            f"/projects/{self.project_name}/folders",
            folder_type="AssetBuild",
            name="child1"
        )
        assert response
        child1 = response["id"]

        response = api.post(
            f"/projects/{self.project_name}/folders",
            folder_type="AssetBuild",
            name="child2"
        )
        assert response
        child2 = response["id"]

        response = api.post(
            f"/projects/{self.project_name}/folders", name="parent")
        assert response
        parent = response["id"]

        response = api.post(
            f"/projects/{self.project_name}/hierarchy",
            id=parent,
            children=[child1, child2]
        )
        assert response

        response = api.get(f"/projects/{self.project_name}/folders/{child1}")
        assert response
        assert response["parentId"] == parent

        response = api.get(f"/projects/{self.project_name}/folders/{child2}")
        assert response
        assert response["parentId"] == parent

        response = api.post(
            f"/projects/{self.project_name}/hierarchy",
            id=None,
            children=[child1]
        )
        assert response

        response = api.get(f"/projects/{self.project_name}/folders/{child1}")
        assert response
        assert response["parentId"] is None

        response = api.get(f"/projects/{self.project_name}/folders/{child2}")
        assert response
        assert response["parentId"] == parent
