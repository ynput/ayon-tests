import uuid
from tests.fixtures import api, PROJECT_NAME


def create_uuid() -> str:
    """Create UUID without hyphens."""
    return uuid.uuid1().hex


def test_operations(api):
    # Create

    parent_id = create_uuid()
    product_id = create_uuid()
    version_id = create_uuid()
    representation_id = create_uuid()
    operations = [
        {
            "type": "create",
            "entityType": "folder",
            "entityId": parent_id,
            "data": {"name": "test_folder1"},
        },
        {
            "type": "create",
            "entityType": "folder",
            "data": {
                "name": "test_folder2",
                "folderType": "Asset",
                "parentId": parent_id,
            },
        },
        {
            "type": "create",
            "entityType": "product",
            "entityId": product_id,
            "data": {
                "name": "test_product",
                "folderId": parent_id,
                "productType": "test",
            },
        },
        {
            "type": "create",
            "entityType": "version",
            "entityId": version_id,
            "data": {
                "productId": product_id,
                "version": 1,
            },
        },
        {
            "type": "create",
            "entityType": "representation",
            "entityId": representation_id,
            "data": {
                "versionId": version_id,
                "name": "test",
            },
        },
    ]

    result = api.post(
        f"/projects/{PROJECT_NAME}/operations",
        operations=operations,
        canFail=False,
    )

    assert result
    assert result.data["success"]

    ids = [x["entityId"] for x in result.data["operations"]]

    assert len(ids) == len(operations)

    for i, id in enumerate(ids):
        response = api.get(
            f"/projects/{PROJECT_NAME}/{operations[i]['entityType']}s/{id}"
        )
        assert response
        assert response.data.get("name") == operations[i]["data"].get("name")

        if operations[i]["entityType"] == "version":
            assert response.data.get("author") == "admin"

    #
    # Update
    #

    operations = [
        {
            "type": "update",
            "entityType": "folder",
            "entityId": ids[0],
            "data": {"name": "test_folder1_edited"},
        },
        {
            "type": "update",
            "entityType": "folder",
            "entityId": ids[1],
            "data": {"name": "test_folder2_edited"},
        },
    ]

    result = api.post(
        f"/projects/{PROJECT_NAME}/operations",
        operations=operations,
        canFail=False,
    )

    assert result
    assert result.data["success"]

    ids = [x["entityId"] for x in result.data["operations"]]

    for i, id in enumerate(ids):
        response = api.get(f"/projects/{PROJECT_NAME}/folders/{id}")
        assert response
        assert response.data["name"] == operations[i]["data"]["name"]

    #
    # Rollback
    #

    operations = [
        {
            "type": "update",
            "entityType": "folder",
            "entityId": ids[0],
            "data": {"name": "wont_be_saved"},
        },
        {
            "type": "update",
            "entityType": "folder",
            "entityId": ids[1],
            "data": {
                "name": "meh",
                "folderType": "THIS IS WRONG AND SHOULD CAUSE A ROLLBACK",
            },
        },
    ]

    result = api.post(
        f"/projects/{PROJECT_NAME}/operations",
        operations=operations,
        canFail=False,
    )

    assert not result.data["success"]
    assert result.data["operations"][0]["success"] is True
    assert result.data["operations"][1]["success"] is False

    response = api.get(f"/projects/{PROJECT_NAME}/folders/{ids[0]}")
    assert response
    assert response.data["name"] == "test_folder1_edited"

    response = api.get(f"/projects/{PROJECT_NAME}/folders/{ids[1]}")
    assert response
    assert response.data["name"] == "test_folder2_edited"

    #
    # Delete
    #

    # Reverse the order to ensure that the parent is deleted last
    operations = [
        {
            "type": "delete",
            "entityType": "folder",
            "entityId": ids[0],
        },
    ]

    result = api.post(
        f"/projects/{PROJECT_NAME}/operations",
        operations=operations,
        canFail=False,
    )

    # This is expected to fail because the parent folder is not empty
    assert result
    assert result.data["success"] is False

    # Try update the same entity multiple times

    operations = [
        {
            "type": "update",
            "entityType": "folder",
            "entityId": ids[0],
            "data": {"name": "test_folder1_edited"},
        },
        {
            "type": "update",
            "entityType": "folder",
            "entityId": ids[0],
            "data": {"name": "test_folder1_edited_again"},
        },
    ]

    result = api.post(
        f"/projects/{PROJECT_NAME}/operations",
        operations=operations,
        canFail=False,
    )

    # This MUST fail
    assert result.status == 400, "Expected a 400 error"

    # Delete product and versions:

    operations = [
        {
            "type": "delete",
            "entityType": "representation",
            "entityId": representation_id,
        },
        {
            "type": "delete",
            "entityType": "version",
            "entityId": version_id,
        },
        {
            "type": "delete",
            "entityType": "product",
            "entityId": product_id,
        },
    ]

    result = api.post(
        f"/projects/{PROJECT_NAME}/operations",
        operations=operations,
        canFail=False,
    )

    assert result
    assert result.data["success"]

    # now try to delete the folder again

    operations = [
        {
            "type": "delete",
            "entityType": "folder",
            "entityId": ids[0],
        },
    ]

    result = api.post(
        f"/projects/{PROJECT_NAME}/operations",
        operations=operations,
        canFail=False,
    )

    assert result
    assert result.data["success"]

    ids = [x["entityId"] for x in result.data["operations"]]
    for id in ids:
        response = api.get(f"/projects/{PROJECT_NAME}/folders/{id}")
        assert not response


def test_hierarchical_attributes(api):
    root_id = create_uuid()
    folder_id = create_uuid()
    asset_id = create_uuid()

    operations = [
        {
            "type": "create",
            "entityType": "folder",
            "entityId": root_id,
            "data": {
                "name": "test_root",
                "attrib": {"resolutionWidth": 1280},
            },
        },
        {
            "type": "create",
            "entityType": "folder",
            "entityId": folder_id,
            "data": {
                "name": "test_folder",
                "parentId": root_id,
                "attrib": {"resolutionHeight": 720},
            },
        },
        {
            "type": "create",
            "entityType": "folder",
            "entityId": asset_id,
            "data": {
                "name": "test_asset",
                "parentId": folder_id,
                "folderType": "Asset",
                "attrib": {"fps": 24},
            },
        },
    ]

    result = api.post(
        f"/projects/{PROJECT_NAME}/operations",
        operations=operations,
        canFail=False,
    )

    # This is expected to fail, because there is a product in the
    # one of the folders
    assert result
    assert result.data["success"]

    # Check that the attributes are set correctly
    response = api.get(f"/projects/{PROJECT_NAME}/folders/{asset_id}")
    assert response
    assert response.data["attrib"]["resolutionWidth"] == 1280
    assert response.data["attrib"]["resolutionHeight"] == 720
    assert response.data["attrib"]["fps"] == 24
