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

        # response = api.delete(f"/projects/{self.project_name}")
        # assert response.status == 204
        api.logout()

    def test_folder_thumbnail(self, api):
        response = api.post(
            f"projects/{self.project_name}/folders",
            name="testicek",
            folderType="AssetBuild",
        )
        assert response

        folder_id = response.data["id"]

        response = api.raw_post(
            f"projects/{self.project_name}/folders/{folder_id}/thumbnail",
            mime="image/png",
            data=THUMB_DATA1,
        )
        assert response

        response = api.raw_get(
            f"projects/{self.project_name}/folders/{folder_id}/thumbnail"
        )
        assert response == THUMB_DATA1

        # Update thumbnail

        response = api.raw_post(
            f"projects/{self.project_name}/folders/{folder_id}/thumbnail",
            mime="image/png",
            data=THUMB_DATA2,
        )
        assert response

        response = api.raw_get(
            f"projects/{self.project_name}/folders/{folder_id}/thumbnail"
        )
        assert response == THUMB_DATA2
