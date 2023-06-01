from tests.fixtures import api, PROJECT_NAME


def test_statuses(api):

    res = api.patch(
        f"/projects/{PROJECT_NAME}",
        statuses=[
            {"name": "status1", "color": "#ff0000", "original_name": "Unknown"},
            {"name": "status2", "color": "#00ff00"},
        ],
    )
    assert res

    res = api.get(f"/projects/{PROJECT_NAME}")
    assert res["statuses"] == [
        {"name": "status1", "color": "#ff0000"},
        {"name": "status2", "color": "#00ff00"},
    ]

    entities = {}
    res = api.post(
        f"/projects/{PROJECT_NAME}/folders",
        name="folder",
        folderType="Folder",
    )

    assert res
    entities["folder"] = res["id"]

    res = api.post(
        f"/projects/{PROJECT_NAME}/products",
        name="product",
        productType="the_simpsons",
        folderId=entities["folder"],
    )

    assert res
    entities["product"] = res["id"]

    res = api.post(
        f"/projects/{PROJECT_NAME}/versions",
        version=1,
        productId=entities["product"],
    )

    assert res
    entities["version"] = res["id"]

    res = api.post(
        f"/projects/{PROJECT_NAME}/representations",
        name="representation",
        versionId=entities["version"],
    )

    assert res
    entities["representation"] = res["id"]

    for entity_type, entity_id in entities.items():
        res = api.get(f"/projects/{PROJECT_NAME}/{entity_type}s/{entity_id}")
        assert res
        assert res["status"] == "status1"

        res = api.patch(
            f"/projects/{PROJECT_NAME}/{entity_type}s/{entity_id}",
            status="status2",
        )

        assert res
        res = api.get(f"/projects/{PROJECT_NAME}/{entity_type}s/{entity_id}")

        assert res
        assert res["status"] == "status2"

        res = api.patch(
            f"/projects/{PROJECT_NAME}/{entity_type}s/{entity_id}",
            status="status3",
        )
        assert not res

    res = api.patch(
        f"/projects/{PROJECT_NAME}",
        statuses=[
            {"name": "newstatus", "color": "#ff00ff", "original_name": "status2"},
            {"name": "status1", "color": "#0000ff"},
        ],
    )
    assert res

    res = api.get(f"/projects/{PROJECT_NAME}")
    assert res
    assert res["statuses"] == [
        {"name": "newstatus", "color": "#ff00ff"},
        {"name": "status1", "color": "#0000ff"},
    ]

    for entity_type, entity_id in entities.items():
        res = api.get(f"/projects/{PROJECT_NAME}/{entity_type}s/{entity_id}")
        assert res
        assert res["status"] == "newstatus"
