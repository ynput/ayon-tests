import pytest

from client.api import API


class TestFolderTypes:
    project_name = "test_folder_types"

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

    def test_folder_types(self, api):
        """folder_types table tests"""

        # From the setup, we should have AssetBuild folder type.
        # Ensure that it is there.

        response = api.get(f"/projects/{self.project_name}")
        assert response
        assert "AssetBuild" in response.data["folderTypes"]

        # Create a folder of AssetBuild type
        response = api.post(
            f"projects/{self.project_name}/folders",
            name="test_folder",
            folderType="AssetBuild"
        )
        assert response

        # Get the id of the newly created folder
        folder_id = response["id"]

        # Ensure that the folder is there and has the correct type
        response = api.get(
            f"projects/{self.project_name}/folders/{folder_id}"
        )
        assert response
        assert response["folderType"] == "AssetBuild"

        # Change folder name by patching the project
        # Original name (which is the dict key) is used for the
        # "where" condition. Special "name" value is used for
        # replacement, and the key is then removed from the dict.

        response = api.patch(
            f"projects/{self.project_name}",
            folder_types={"AssetBuild": {"name": "Asset"}}
        )
        assert response

        # Check if folder_typoe was changed on the folder too

        response = api.get(
            f"projects/{self.project_name}/folders/{folder_id}"
        )
        assert response
        assert response["folderType"] == "Asset"

        # Add a few more folder types

        response = api.patch(
            f"projects/{self.project_name}",
            folderTypes={
                "Sequence": {"icon": "sequence"},
                "Shot": {"icon": "shot"}
            }
        )
        assert response

        # Check if folder types were added

        response = api.get(f"projects/{self.project_name}")
        assert response

        folder_types = response["folderTypes"]
        assert len(folder_types) == 3
        assert "Asset" in folder_types
        assert "Sequence" in folder_types
        assert "Shot" in folder_types
        assert "AssetBuild" not in folder_types

        assert type(folder_types["Shot"]) is dict

        # Delete a folder type by setting its data field to None

        response = api.patch(
            f"projects/{self.project_name}",
            folderTypes={"Sequence": None}
        )
        assert response

        response = api.get(f"projects/{self.project_name}")
        assert response

        folder_types = response["folderTypes"]
        assert len(folder_types) == 2
        assert "Asset" in folder_types
        assert "Shot" in folder_types
        assert "Folder" not in folder_types

        # Update folder_type data

        response = api.patch(
            f"projects/{self.project_name}",
            folderTypes={"Shot": {"icon": "shot2"}}
        )
        assert response

        response = api.get(f"projects/{self.project_name}")
        assert response

        folder_types = response["folderTypes"]
        assert type(folder_types) is dict
        assert len(folder_types) == 2
        assert "Shot" in folder_types
        assert folder_types["Shot"]["icon"] == "shot2"
