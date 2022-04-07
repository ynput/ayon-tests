import pytest

from client.api import API


class TestFolders:
    project_name = "test_folders"

    @pytest.fixture(scope="class")
    def api(self):
        api = API.login("admin", "admin")

        response = api.delete(f"/projects/{self.project_name}")

        response = api.put(
            f"/projects/{self.project_name}", folder_types={"AssetBuild": {}}
        )
        assert response.status == 201

        yield api

        response = api.delete(f"/projects/{self.project_name}")
        assert response.status == 204
        api.logout()

    def test_folders(self, api):
        response = api.post(
            f"projects/{self.project_name}/folders",
            name="testicek",
            folderType="AssetBuild",
        )
        assert response

        folder_id = response.data["id"]

        # patching

        response = api.patch(
            f"projects/{self.project_name}/folders/{folder_id}", name="testicek2"
        )
        assert response

    def test_unique_names(self, api):
        """One parent folder cannot have two children with the same name"""

        response = api.post(
            f"projects/{self.project_name}/folders",
            name="root",
            folderType="AssetBuild",
        )
        assert response
        root_id = response["id"]

        response = api.post(
            f"projects/{self.project_name}/folders",
            name="test",
            folderType="AssetBuild",
            parent_id=root_id,
        )
        assert response

        response = api.post(
            f"projects/{self.project_name}/folders",
            name="test",
            folderType="AssetBuild",
            parent_id=root_id,
        )
        assert not response

        response = api.post(
            f"projects/{self.project_name}/folders",
            name="test",
            folderType="AssetBuild",
            parent_id=root_id,
            active=False,
        )
        assert response

        response = api.post(
            f"projects/{self.project_name}/folders",
            name="root",
            folderType="AssetBuild",
        )
        assert not response
