import pytest

from client.api import API

THUMB_DATA1 = b"thisisaveryrandomthumbnailcontent"
THUMB_DATA2 = b"thisihbhihjhuuyiooanothbnlcontent"


class TestThumbnails:
    project_name = "test_thumbnails"

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
        api.logout()

    def test_folder_thumbnail(self, api):
        response = api.post(
            f"projects/{self.project_name}/folders",
            name="testicek",
            folderType="AssetBuild",
        )
        assert response
        folder_id = response.data["id"]

        # Ensure we cannot create an empty thumbnail

        assert not api.raw_post(
            f"projects/{self.project_name}/folders/{folder_id}/thumbnail",
            mime="image/png",
            data=b"",
        )

        # Create a thumbnail for the folder

        response = api.raw_post(
            f"projects/{self.project_name}/folders/{folder_id}/thumbnail",
            mime="image/png",
            data=THUMB_DATA1,
        )
        assert response

        # Ensure the thumbnail is there

        response = api.raw_get(
            f"projects/{self.project_name}/folders/{folder_id}/thumbnail"
        )
        assert response == THUMB_DATA1

        # Get the id of the thumbnail (we can re-use it later)

        thumb1_id = api.get(
            f"projects/{self.project_name}/folders/{folder_id}",
        ).data["thumbnailId"]

        # Update thumbnail

        response = api.raw_post(
            f"projects/{self.project_name}/folders/{folder_id}/thumbnail",
            mime="image/png",
            data=THUMB_DATA2,
        )
        assert response

        # Ensure the thumbnail changed

        response = api.raw_get(
            f"projects/{self.project_name}/folders/{folder_id}/thumbnail"
        )
        assert response == THUMB_DATA2

        # Let the folder use the old thumbnail

        response = api.patch(
            f"projects/{self.project_name}/folders/{folder_id}",
            thumbnail_id=thumb1_id,
        )
        assert response

        # Ensure the thumbnail is switched to the old one

        response = api.raw_get(
            f"projects/{self.project_name}/folders/{folder_id}/thumbnail"
        )
        assert response == THUMB_DATA1

    def test_version_thumbnail(self, api):

        # Create folder/subset/version

        response = api.post(
            f"projects/{self.project_name}/folders",
            name="test2",
            folderType="AssetBuild",
        )
        assert response

        folder_id = response.data["id"]

        response = api.post(
            f"projects/{self.project_name}/subsets",
            name="test2s",
            family="theSopranos",
            folderId=folder_id,
        )
        assert response

        subset_id = response.data["id"]

        response = api.post(
            f"projects/{self.project_name}/versions",
            version=1,
            subsetId=subset_id,
        )

        version_id = response.data["id"]

        # Create thumbnail for the version

        response = api.raw_post(
            f"projects/{self.project_name}/versions/{version_id}/thumbnail",
            mime="image/png",
            data=THUMB_DATA1,
        )
        assert response

        # Verify that the thumbnail is there

        response = api.raw_get(
            f"projects/{self.project_name}/versions/{version_id}/thumbnail"
        )
        assert response == THUMB_DATA1
