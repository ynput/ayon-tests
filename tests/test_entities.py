import pytest

from client.api import API


class TestEntities:
    project_name = "test_entities"
    representation_name = "boob"
    file_hash = "aaaaaaaabbbbbbbbccccccccdddddddd"
    file_size = 123456789

    @pytest.fixture(scope="class")
    def api(self):
        api = API.login("admin", "admin")
        response = api.delete(f"/projects/{self.project_name}")

        response = api.put(
            f"/projects/{self.project_name}",
            folder_types={"AssetBuild": {}}
        )
        assert response.status == 201

        yield api

        response = api.delete(f"/projects/{self.project_name}")
        assert response.status == 204
        api.logout()

    @pytest.fixture
    def folder_id(self, api):
        response = api.post(
            f"projects/{self.project_name}/folders",
            name="test_folder",
            folderType="AssetBuild"
        )
        assert response
        folder_id = response.data["id"]
        yield folder_id
        response = api.delete(f"projects/{self.project_name}/folders/{folder_id}")
        assert response

    @pytest.fixture
    def subset_id(self, api, folder_id):
        response = api.post(
            f"projects/{self.project_name}/subsets",
            folderId=folder_id,
            name="test_subset",
            family="TheSimpsons"
        )
        assert response
        subset_id = response.data["id"]
        yield subset_id
        response = api.delete(f"projects/{self.project_name}/subsets/{subset_id}")
        assert response

    @pytest.fixture
    def version_id(self, api, subset_id):
        response = api.post(
            f"projects/{self.project_name}/versions",
            subsetId=subset_id,
            version=42,
        )
        assert response
        version_id = response.data["id"]
        yield version_id
        response = api.delete(f"projects/{self.project_name}/versions/{version_id}")
        assert response

    @pytest.fixture
    def representation_id(self, api, version_id):
        files = {
            self.file_hash: {
                "hash": self.file_hash,
                "path": "/some/path",
                "size": self.file_size
            }
        }
        response = api.post(
            f"projects/{self.project_name}/representations",
            versionId=version_id,
            name=self.representation_name,
            data={"files": files}
        )
        assert response
        version_id = response.data["id"]
        yield version_id

    def test_folder(self, api, folder_id):
        response = api.patch(
            f"projects/{self.project_name}/folders/{folder_id}",
            name="foobar"
        )
        assert response

    def test_subset(self, api, subset_id):
        response = api.patch(
            f"projects/{self.project_name}/subsets/{subset_id}",
            family="Sopranos"
        )
        assert response

    def test_representation(self, api, representation_id):
        """Ensure patching won't affect data already stored"""
        repre_url = f"projects/{self.project_name}/representations/{representation_id}"
        response = api.patch(repre_url, data={"randomkey": "abcd"})
        assert response

        repre = api.get(repre_url)
        assert repre
        assert "randomkey" in repre["data"]
        assert "files" in repre["data"]
        assert repre["data"]["files"][self.file_hash]["size"] == self.file_size

    def test_site_sync_params(self, api, representation_id):
        response = api.get(f"projects/{self.project_name}/sitesync/params")
        assert response
        assert response["names"] == [self.representation_name]
        assert response["count"] == 1

    def test_site_sync_state(self, api, representation_id):
        response = api.get(
            f"projects/{self.project_name}/sitesync/state",
            localSite="local",
            remoteSite="remote"
        )
        assert response
        assert len(response["representations"]) == 1
        state_row = response["representations"][0]

        assert state_row["representationId"] == representation_id
        assert state_row["size"] == self.file_size
        assert state_row["localStatus"] == -1
        assert state_row["remoteStatus"] == -1
        assert state_row["files"] is None

        response = api.post(
            f"projects/{self.project_name}/sitesync/state/{representation_id}/local",
            files=[{
                "fileHash": self.file_hash,
                "size": 5,
                "status": 0  # in progress
            }]
        )
        assert response

        #

        response = api.get(
            f"projects/{self.project_name}/sitesync/state",
            localSite="local",
            remoteSite="remote"
        )
        assert response
        state_row = response["representations"][0]
        assert state_row["localStatus"] == 0

        response = api.get(
            f"projects/{self.project_name}/sitesync/state",
            localSite="local",
            remoteSite="remote",
            representationId=representation_id
        )
        assert response
        assert len(response["representations"]) == 1
        state_row = response["representations"][0]

        assert type(state_row["files"]) is list
        assert len(state_row["files"]) == 1
