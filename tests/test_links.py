import pytest

from client.api import API


class TestLinks:
    project_name = "test_links"

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

    def test_link_types(self, api):
        assert api.put(
            f"/projects/{self.project_name}/links/types/breakdown|folder|subset"
        )

        response = api.get(f"/projects/{self.project_name}/links/types")
        assert response.status == 200
        assert response.data["types"] == [
            {"name": "breakdown|folder|subset", "data": {}}
        ]

        assert api.delete(
            f"/projects/{self.project_name}/links/types/breakdown|folder|subset"
        )

        response = api.get(f"/projects/{self.project_name}/links/types")
        assert response.status == 200
        assert response.data["types"] == []

        return

    def test_link_types_invalid(self, api):
        bad_examples = [
            "whatever",
            "what|ever",
            "wha|t|ev|er",
            "breakdown|folder|subset|",
            "breakdown|folder|subset|what",
            "breakdown|what|ever",
            "breakdown|folder|what",
        ]

        for lname in bad_examples:
            assert not api.put(f"/projects/{self.project_name}/links/types/{lname}")

    def test_links(self, api):
        response = api.post(
            f"projects/{self.project_name}/folders",
            name="f1",
            folderType="AssetBuild",
        )
        assert response
        f1 = response.data["id"]

        response = api.post(
            f"projects/{self.project_name}/folders",
            name="f2",
            folderType="AssetBuild",
        )
        assert response
        f2 = response.data["id"]

        assert api.put(
            f"/projects/{self.project_name}/links/types/breakdown|folder|subset"
        )

        # Should fail because f2 is not a subset
        assert not api.post(
            f"/projects/{self.project_name}/links",
            link="breakdown|folder|subset",
            input=f1,
            output=f2,
        )

        # Should fail because folder-folder link is not yet defined
        assert not api.post(
            f"/projects/{self.project_name}/links",
            link="breakdown|folder|folder",
            input=f1,
            output=f2,
        )

        assert api.put(
            f"/projects/{self.project_name}/links/types/breakdown|folder|folder"
        )

        # Should be ok
        assert api.post(
            f"/projects/{self.project_name}/links",
            link="breakdown|folder|folder",
            input=f1,
            output=f2,
        )

        # Should fail, because we already have this link
        assert not api.post(
            f"/projects/{self.project_name}/links",
            link="breakdown|folder|folder",
            input=f1,
            output=f2,
        )
