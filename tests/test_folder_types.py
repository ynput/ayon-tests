from tests.fixtures import api, PROJECT_NAME

assert api


def test_folder_types(api):
    """folder_types table tests"""

    # From the setup, we should have AssetBuild folder type.
    # Ensure that it is there.

    response = api.get(f"/projects/{PROJECT_NAME}")
    assert response
    assert "Asset" in response.data["folderTypes"]

    # Create a folder of AssetBuild type
    response = api.post(
        f"projects/{PROJECT_NAME}/folders",
        name="test_folder",
        folderType="Asset",
    )
    assert response

    # Get the id of the newly created folder
    folder_id = response["id"]

    # Ensure that the folder is there and has the correct type
    response = api.get(f"projects/{PROJECT_NAME}/folders/{folder_id}")
    assert response
    assert response["folderType"] == "Asset"

    # Change folder name by patching the project
    # Original name (which is the dict key) is used for the
    # "where" condition. Special "name" value is used for
    # replacement, and the key is then removed from the dict.

    response = api.patch(
        f"projects/{PROJECT_NAME}",
        folder_types={"Asset": {"name": "AssetType"}},
    )
    assert response

    # Check if folder_typoe was changed on the folder too

    response = api.get(f"projects/{PROJECT_NAME}/folders/{folder_id}")
    assert response
    assert response["folderType"] == "AssetType"

    # Add a few more folder types

    response = api.patch(
        f"projects/{PROJECT_NAME}",
        folderTypes={"Sequence": {"icon": "sequence"}, "Shot": {"icon": "shot"}},
    )
    assert response

    # Check if folder types were added

    response = api.get(f"projects/{PROJECT_NAME}")
    assert response

    folder_types = response["folderTypes"]
    assert len(folder_types) == 3
    assert "AssetType" in folder_types
    assert "Sequence" in folder_types
    assert "Shot" in folder_types
    assert "Asset" not in folder_types

    assert type(folder_types["Shot"]) is dict

    # Delete a folder type by setting its data field to None

    response = api.patch(f"projects/{PROJECT_NAME}", folderTypes={"Sequence": None})
    assert response

    response = api.get(f"projects/{PROJECT_NAME}")
    assert response

    folder_types = response["folderTypes"]
    assert len(folder_types) == 2
    assert "AssetType" in folder_types
    assert "Shot" in folder_types
    assert "Folder" not in folder_types

    # Update folder_type data

    response = api.patch(
        f"projects/{PROJECT_NAME}", folderTypes={"Shot": {"icon": "shot2"}}
    )
    assert response

    response = api.get(f"projects/{PROJECT_NAME}")
    assert response

    folder_types = response["folderTypes"]
    assert type(folder_types) is dict
    assert len(folder_types) == 2
    assert "Shot" in folder_types
    assert folder_types["Shot"]["icon"] == "shot2"
