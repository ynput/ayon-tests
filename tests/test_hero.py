from tests.fixtures import api, PROJECT_NAME

assert api


def test_hero(api):
    response = api.post(
        f"projects/{PROJECT_NAME}/folders",
        name="test",
        folderType="Asset",
    )
    assert response

    folder_id = response.data["id"]

    # create a subset

    response = api.post(
        f"projects/{PROJECT_NAME}/subsets",
        folderId=folder_id,
        name="test",
        family="whatever",
    )

    assert response
    subset_id = response.data["id"]

    # create a hero version

    response = api.post(
        f"projects/{PROJECT_NAME}/versions", subsetId=subset_id, version=-1
    )

    assert response

    first_version_id = response.data["id"]

    # attempt to create another hero version

    response = api.post(
        f"projects/{PROJECT_NAME}/versions", subsetId=subset_id, version=-2
    )

    assert not response

    # create a non-hero version
    response = api.post(
        f"projects/{PROJECT_NAME}/versions", subsetId=subset_id, version=2
    )

    assert response
    second_version_id = response.data["id"]

    # attempt to promote the non-hero version to hero
    response = api.patch(
        f"projects/{PROJECT_NAME}/versions/{second_version_id}",
        version=-2,
    )

    assert not response

    # delete the first version

    response = api.delete(f"projects/{PROJECT_NAME}/versions/{first_version_id}")
    assert response

    # create another hero version

    # now that the first version is deleted, we should be able to promote the
    # second version to hero
    response = api.patch(
        f"projects/{PROJECT_NAME}/versions/{second_version_id}",
        version=-2,
    )

    assert response
