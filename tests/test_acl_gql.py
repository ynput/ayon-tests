from tests.fixtures import api, PROJECT_NAME

assert api


def create_entity(api, entity_type: str, **kwargs):
    response = api.post(f"projects/{PROJECT_NAME}/{entity_type}s", **kwargs)
    assert response
    return response.data["id"]


def test_access_ok(api):
    folder_id = create_entity(
        api,
        "folder",
        name="folder",
        folderType="Asset",
    )
    product_id = create_entity(
        api,
        "product",
        name="test",
        productType="thesimpsons",
        folderId=folder_id,
    )
    version_id = create_entity(
        api,
        "version",
        version=42,
        productId=product_id,
    )
    representation_id = create_entity(
        api,
        "representation",
        name="pptx",
        versionId=version_id,
    )

    assert representation_id
