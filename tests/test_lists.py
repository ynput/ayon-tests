import sys
import time
import uuid
from tests.fixtures import api, PROJECT_NAME


def create_uuid() -> str:
    """Create UUID without hyphens."""
    return uuid.uuid1().hex

folder_ids = [create_uuid() for _ in range(5)]
list_id = create_uuid()



def test_create_folders(api):

    # Create a bunch of folders

    operations = []
    for i, folder_id in enumerate(folder_ids):
        operations.append(
            {
                "type": "create",
                "entityType": "folder",
                "entityId": folder_id,
                "data": {"name": f"folder{i}", "folderType": "Folder" },
            }
        )
    result = api.post(
        f"/projects/{PROJECT_NAME}/operations",
        operations=operations,
        canFail=False,
    )

    assert result
    assert result.data["success"]

    # Create a list of the folders

    items = []
    for i, folder_id in enumerate(folder_ids):
        items.append(
            {
                "entityType": "folder", 
                "entityId": folder_id, 
                "label": f"item{i}", 
                "attrib": {"mykey": f"myvalue{i}"}
            }
        )

    payload = {
        "id": list_id,
        "label": "My List",
        "listType": "FolderList",
        "items": items
    }

    result = api.post(f"/projects/{PROJECT_NAME}/lists", **payload)

    assert result
    assert result.data.get("id") == list_id

    # Get the list

    result = api.get(f"/projects/{PROJECT_NAME}/lists/{list_id}")

    assert result
    summary = result.data["data"]["summary"]
    assert summary.get("folders") == len(folder_ids), f"Folder count mismatch {summary}"

    item_ids = [item["id"] for item in result.data["items"]]

    # move the third folder to the top

    payload = {
        "position": 0,
        "attrib": {"mykey": None, "newkey": "newvalue"}
    }

    result = api.patch(
        f"/projects/{PROJECT_NAME}/lists/{list_id}/items/{item_ids[2]}", 
        **payload
    )

    assert result

    # get the list again

    result = api.get(f"/projects/{PROJECT_NAME}/lists/{list_id}")

    assert result

    updated_item_ids = [item["id"] for item in result.data["items"]]

    assert updated_item_ids[0] == item_ids[2]
    attrib = result.data["items"][0]["attrib"]

    assert "mykey" not in attrib
    assert attrib.get("newkey") == "newvalue"


    # Delete the list

    result = api.delete(f"/projects/{PROJECT_NAME}/lists/{list_id}")
    assert result

    # Ensure the list is gone

    result = api.get(f"/projects/{PROJECT_NAME}/lists/{list_id}")
    assert not result




    # Try creating a list with unsupported entity type

    items.append(
        {
            "entityType": "representation", 
            "entityId": folder_id, 
            "label": f"item{i}", 
            "attrib": {"mykey": f"myvalue{i}"}
        }
    )

    payload = {
        "id": list_id,
        "label": "My List",
        "listType": "FolderList",
        "items": items
    }

    result = api.post(f"/projects/{PROJECT_NAME}/lists", **payload)

    assert not result

