from tests.fixtures import api, PROJECT_NAME

assert api


def test_link_types(api):
    assert api.put(f"/projects/{PROJECT_NAME}/links/types/breakdown|folder|subset")

    response = api.get(f"/projects/{PROJECT_NAME}/links/types")
    assert response.status == 200
    types = response.data["types"]
    assert len(types) == 1
    assert types[0]["name"] == "breakdown|folder|subset"

    assert api.delete(f"/projects/{PROJECT_NAME}/links/types/breakdown|folder|subset")

    response = api.get(f"/projects/{PROJECT_NAME}/links/types")
    assert response.status == 200
    assert response.data["types"] == []

    return


def test_link_types_invalid(api):
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
        assert not api.put(f"/projects/{PROJECT_NAME}/links/types/{lname}")


def test_links(api):
    response = api.post(
        f"projects/{PROJECT_NAME}/folders",
        name="f1",
        folderType="Asset",
    )
    assert response
    f1 = response.data["id"]

    response = api.post(
        f"projects/{PROJECT_NAME}/folders",
        name="f2",
        folderType="Asset",
    )
    assert response
    f2 = response.data["id"]

    assert api.put(f"/projects/{PROJECT_NAME}/links/types/breakdown|folder|subset")

    # Should fail because f2 is not a subset
    assert not api.post(
        f"/projects/{PROJECT_NAME}/links",
        link="breakdown|folder|subset",
        input=f1,
        output=f2,
    )

    # Should fail because folder-folder link is not yet defined
    assert not api.post(
        f"/projects/{PROJECT_NAME}/links",
        link="breakdown|folder|folder",
        input=f1,
        output=f2,
    )

    assert api.put(f"/projects/{PROJECT_NAME}/links/types/breakdown|folder|folder")

    # Should be ok
    assert api.post(
        f"/projects/{PROJECT_NAME}/links",
        link="breakdown|folder|folder",
        input=f1,
        output=f2,
    )

    # Should fail, because we already have this link
    assert not api.post(
        f"/projects/{PROJECT_NAME}/links",
        link="breakdown|folder|folder",
        input=f1,
        output=f2,
    )

    # create a subset
    response = api.post(
        f"/projects/{PROJECT_NAME}/subsets",
        name="s1",
        folder_id=f1,
        family="thegriffins",
    )
    assert response
    s1 = response.data["id"]

    # try to create subset-folder link (which should fail)
    assert not api.post(
        f"/projects/{PROJECT_NAME}/links",
        link="breakdown|subset|folder",
        input=s1,
        output=f2,
    )

    # create a folder-subset link
    assert api.post(
        f"/projects/{PROJECT_NAME}/links",
        link="breakdown|folder|subset",
        input=f1,
        output=s1,
    )

    # create a similar link, but wong folder_id
    assert not api.post(
        f"/projects/{PROJECT_NAME}/links",
        link="breakdown|folder|subset",
        input="1234abcd" * 4,
        output=s1,
    )

    # create a similar link, but wong subset_id
    assert not api.post(
        f"/projects/{PROJECT_NAME}/links",
        link="breakdown|folder|subset",
        input=f2,
        output="1234abcd" * 4,
    )
