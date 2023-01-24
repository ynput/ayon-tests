from tests.fixtures import api, PROJECT_NAME


def test_tags(api):

    res = api.patch(
        f"/projects/{PROJECT_NAME}",
        tags=[{"name": "tag1", "color": "#ff0000"}],
    )

    assert res

    # build a hierarchy of folder / subset / version / representation

    entities = {}
    res = api.post(
        f"/projects/{PROJECT_NAME}/folders",
        name="folder",
        folderType="Folder",
        tags=["tag1"],
    )

    assert res
    entities["folder"] = res["id"]

    res = api.post(
        f"/projects/{PROJECT_NAME}/subsets",
        name="subset",
        family="the_simpsons",
        folderId=entities["folder"],
        tags=["tag1"],
    )

    assert res
    entities["subset"] = res["id"]

    res = api.post(
        f"/projects/{PROJECT_NAME}/versions",
        version=1,
        subsetId=entities["subset"],
        tags=["tag1"],
    )

    assert res
    entities["version"] = res["id"]

    res = api.post(
        f"/projects/{PROJECT_NAME}/representations",
        name="representation",
        versionId=entities["version"],
        tags=["tag1"],
    )

    assert res
    entities["representation"] = res["id"]

    for entity_type, entity_id in entities.items():
        res = api.get(f"/projects/{PROJECT_NAME}/{entity_type}s/{entity_id}")

        assert res
        assert res.data["tags"] == ["tag1"]

        res = api.patch(
            f"/projects/{PROJECT_NAME}/{entity_type}s/{entity_id}",
            tags=["tag2"],
        )

        assert res

        res = api.get(f"/projects/{PROJECT_NAME}/{entity_type}s/{entity_id}")

        assert res
        assert res.data["tags"] == ["tag2"]
