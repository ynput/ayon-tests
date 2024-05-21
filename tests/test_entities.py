import pytest
from tests.fixtures import api, PROJECT_NAME

assert api


REPRESENTATION_NAME = "boob"
FILE_HASH = "aaaaaaaabbbbbbbbccccccccdddddddd"
FILE_SIZE = 123456789

FILES = [
    {
        "id": "file1",
        "name": "my_file001.png",
        "path": "/path/to/my_file001.png",
        "size": 123456789,
        "hash": "aaaaaaaabbbbbbbbccccccccdddddddd",
    },
    {
        "id": "file2",
        "name": "my_file002.png",
        "path": "/path/to/my_file002.png",
        "size": 123456789,
        "hash": "aaaaaaaabbbbbbbbccccccccdddddddd",
    },
]


def patch_and_get(api, url, **kwargs):
    response = api.patch(url, **kwargs)
    assert response
    result = api.get(url)
    assert result
    return result.data


@pytest.fixture
def folder_ids(api):
    response = api.post(
        f"projects/{PROJECT_NAME}/folders",
        name="root_folder",
        folderType="Folder",
    )
    assert response
    root_folder_id = response.data["id"]

    response = api.post(
        f"projects/{PROJECT_NAME}/folders",
        name="child_folder",
        folderType="Asset",
        parentId=root_folder_id,
    )
    assert response
    child_folder_id = response.data["id"]

    yield root_folder_id, child_folder_id


@pytest.fixture
def product_id(api, folder_ids):
    folder_id = folder_ids[1]
    response = api.post(
        f"projects/{PROJECT_NAME}/products",
        folderId=folder_id,
        name="test_product",
        productType="TheSimpsons",
    )
    assert response
    product_id = response.data["id"]
    yield product_id
    response = api.delete(f"projects/{PROJECT_NAME}/products/{product_id}")
    # assert response


@pytest.fixture
def task_id(api, folder_ids):
    folder_id = folder_ids[1]
    response = api.post(
        f"projects/{PROJECT_NAME}/tasks",
        folderId=folder_id,
        name="test_task",
        taskType="Generic",
    )
    assert response
    task_id = response.data["id"]
    yield task_id
    response = api.delete(f"projects/{PROJECT_NAME}/tasks/{task_id}")
    # assert response


@pytest.fixture
def version_id(api, product_id):
    response = api.post(
        f"projects/{PROJECT_NAME}/versions",
        productId=product_id,
        version=42,
    )
    assert response
    version_id = response.data["id"]
    yield version_id
    response = api.delete(f"projects/{PROJECT_NAME}/versions/{version_id}")
    # assert response


@pytest.fixture
def representation_id(api, version_id):
    response = api.post(
        f"projects/{PROJECT_NAME}/representations",
        versionId=version_id,
        name=REPRESENTATION_NAME,
        files=FILES,
    )
    assert response
    representation_id = response.data["id"]
    yield representation_id


def test_folder(api, folder_ids):
    folder_id = folder_ids[1]
    result = patch_and_get(
        api,
        f"projects/{PROJECT_NAME}/folders/{folder_id}",
        name="foobar",
        attrib={"resolutionWidth": 1234},
        data={"foo": "bar"},
    )
    assert result["attrib"]["resolutionWidth"] == 1234
    assert result["data"] == {"foo": "bar"}

    result = patch_and_get(
        api,
        f"projects/{PROJECT_NAME}/folders/{folder_id}",
        data={"foo": "baz"},
    )
    assert result["attrib"]["resolutionWidth"] == 1234
    assert result["data"] == {"foo": "baz"}

    result = patch_and_get(
        api,
        f"projects/{PROJECT_NAME}/folders/{folder_id}",
        data={"alpha": "beta"},
    )

    assert result["attrib"]["resolutionWidth"] == 1234
    assert result["data"] == {"alpha": "beta", "foo": "baz"}

    result = patch_and_get(
        api,
        f"projects/{PROJECT_NAME}/folders/{folder_id}",
        data={"alpha": None},
    )
    assert result["data"] == {"foo": "baz"}

    result = patch_and_get(
        api,
        f"projects/{PROJECT_NAME}/folders/{folder_id}",
        label="Foo bar",
    )
    assert result["label"] == "Foo bar"

    result = patch_and_get(
        api,
        f"projects/{PROJECT_NAME}/folders/{folder_id}",
        label=None,
    )
    assert "label" not in result, f"label should be removed, but is {result['label']}"


def test_product(api, product_id):
    response = api.patch(
        f"projects/{PROJECT_NAME}/products/{product_id}", productType="Sopranos"
    )
    assert response

    result = patch_and_get(
        api,
        f"projects/{PROJECT_NAME}/products/{product_id}",
        data={"foo": "baz"},
    )
    assert result["data"] == {"foo": "baz"}

    result = patch_and_get(
        api,
        f"projects/{PROJECT_NAME}/products/{product_id}",
        data={"alpha": "beta"},
    )

    assert result["data"] == {"alpha": "beta", "foo": "baz"}


def test_version(api, version_id):
    response = api.get(f"projects/{PROJECT_NAME}/versions/{version_id}")
    assert response
    assert response.data["version"] == 42
    assert response.data["author"] == "admin"

    response = api.patch(
        f"projects/{PROJECT_NAME}/versions/{version_id}",
        author="john",
    )

    assert response

    response = api.get(f"projects/{PROJECT_NAME}/versions/{version_id}")
    assert response
    assert response.data["version"] == 42
    assert response.data["author"] == "john"


def test_task(api, task_id):
    response = api.patch(
        f"projects/{PROJECT_NAME}/tasks/{task_id}",
        name="walk_the_dog",
        label="Walk the dog",
    )
    assert response


    response = api.patch(
        f"projects/{PROJECT_NAME}/tasks/{task_id}",
        label=None,
    )
    assert response

    response = api.get(f"projects/{PROJECT_NAME}/tasks/{task_id}")
    assert response
    assert "label" not in response.data, f"label should be removed, but is {response.data['label']}"


def test_representation(api, representation_id):
    """Ensure patching won't affect data already stored"""
    repre_url = f"projects/{PROJECT_NAME}/representations/{representation_id}"
    response = api.patch(
        repre_url,
        data={"randomkey": "abcd"},
        attrib={"resolutionWidth": 1234},
    )
    assert response

    repre = api.get(repre_url)
    assert repre

    assert repre.data["attrib"]["resolutionWidth"] == 1234

    response = api.patch(repre_url, attrib={"resolutionWidth": 4321})
    assert response

    repre = api.get(repre_url)
    assert repre

    assert repre.data["attrib"]["resolutionWidth"] == 4321

    assert len(repre["files"]) == 2
    assert repre["files"][0]["id"] == "file1"
    assert repre["files"][1]["id"] == "file2"

    new_files = [
        {
            "id": "file3",
            "name": "my_file003.png",
            "path": "/path/to/my_file003.png",
            "size": 123456789,
            "hash": "aaaaaaaabbbbbbbbccccccccdddddddd",
        },
    ]

    response = api.patch(repre_url, files=new_files)

    repre = api.get(repre_url)
    assert response
    assert len(repre["files"]) == 1
    assert repre["files"][0]["id"] == "file3"


def test_explicit_id(api):
    import uuid

    my_folder_id = uuid.uuid4().hex

    response = api.post(
        f"projects/{PROJECT_NAME}/folders",
        id=my_folder_id,
        name="explicit_id_folder",
        folderType="Folder",
    )
    assert response
    assert response.data["id"] == my_folder_id


@pytest.mark.order(-1)
def test_delete_tree(api, representation_id, folder_ids):
    root_folder_id, child_folder_id = folder_ids

    response = api.delete(f"projects/{PROJECT_NAME}/folders/{root_folder_id}")
    assert not response

    response = api.delete(
        f"projects/{PROJECT_NAME}/folders/{root_folder_id}?force=true"
    )
    assert response
