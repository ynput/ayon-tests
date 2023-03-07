import pytest
from tests.fixtures import api, PROJECT_NAME

assert api


REPRESENTATION_NAME = "boob"
FILE_HASH = "aaaaaaaabbbbbbbbccccccccdddddddd"
FILE_SIZE = 123456789


@pytest.fixture
def folder_id(api):
    response = api.post(
        f"projects/{PROJECT_NAME}/folders",
        name="test_folder",
        folderType="Asset",
    )
    assert response
    folder_id = response.data["id"]
    yield folder_id
    response = api.delete(f"projects/{PROJECT_NAME}/folders/{folder_id}")
    assert response


@pytest.fixture
def subset_id(api, folder_id):
    response = api.post(
        f"projects/{PROJECT_NAME}/subsets",
        folderId=folder_id,
        name="test_subset",
        family="TheSimpsons",
    )
    assert response
    subset_id = response.data["id"]
    yield subset_id
    response = api.delete(f"projects/{PROJECT_NAME}/subsets/{subset_id}")
    assert response


@pytest.fixture
def task_id(api, folder_id):
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
    assert response


@pytest.fixture
def version_id(api, subset_id):
    response = api.post(
        f"projects/{PROJECT_NAME}/versions",
        subsetId=subset_id,
        version=42,
    )
    assert response
    version_id = response.data["id"]
    yield version_id
    response = api.delete(f"projects/{PROJECT_NAME}/versions/{version_id}")
    assert response


@pytest.fixture
def representation_id(api, version_id):
    # files = {
    #     FILE_HASH: {
    #         "hash": FILE_HASH,
    #         "path": "/some/path",
    #         "size": FILE_SIZE,
    #     }
    # }
    response = api.post(
        f"projects/{PROJECT_NAME}/representations",
        versionId=version_id,
        name=REPRESENTATION_NAME,
        # data={"files": files},
    )
    assert response
    version_id = response.data["id"]
    yield version_id


def test_folder(api, folder_id):
    response = api.patch(f"projects/{PROJECT_NAME}/folders/{folder_id}", name="foobar", attrib={"resolutionWidth": 1234})
    assert response

    folder = api.get(f"projects/{PROJECT_NAME}/folders/{folder_id}")
    assert folder
    assert folder.data["attrib"]["resolutionWidth"] == 1234



def test_subset(api, subset_id):
    response = api.patch(
        f"projects/{PROJECT_NAME}/subsets/{subset_id}", family="Sopranos"
    )
    assert response


def test_task(api, task_id):
    response = api.patch(
        f"projects/{PROJECT_NAME}/tasks/{task_id}", name="walk_the_dog"
    )
    assert response


def test_representation(api, representation_id):
    """Ensure patching won't affect data already stored"""
    repre_url = f"projects/{PROJECT_NAME}/representations/{representation_id}"
    response = api.patch(
        repre_url,
        data={"randomkey": "abcd"},
        attrib={"resolutionWidth": 1234},
        files=[
            {
                "id": "1234567890",
                "path": 123,
            }
        ],
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

    # assert len(repre["files"]) == 1

    # response = api.patch(repre_url, files=[{"size": 400}])
    # assert not response


# REMOVED. Site sync is no longer a part of the core API.
#
# def test_site_sync_params(api, representation_id):
#     response = api.get(f"projects/{PROJECT_NAME}/sitesync/params")
#     assert response
#     assert response["names"] == [REPRESENTATION_NAME]
#     assert response["count"] == 1
#
#
# def test_site_sync_state(api, representation_id):
#     response = api.get(
#         f"projects/{PROJECT_NAME}/sitesync/state",
#         localSite="local",
#         remoteSite="remote",
#     )
#     assert response
#     assert len(response["representations"]) == 1
#     state_row = response["representations"][0]
#
#     assert state_row["representationId"] == representation_id
#     assert state_row["size"] == FILE_SIZE
#     assert state_row["localStatus"]["status"] == -1
#     assert state_row["remoteStatus"]["status"] == -1
#     assert state_row["files"] is None
#
#     response = api.post(
#         f"projects/{PROJECT_NAME}/sitesync/state/{representation_id}/local",
#         files=[{"fileHash": FILE_HASH, "size": 5, "status": 0}],  # in progress
#     )
#     assert response
#
#     #
#
#     response = api.get(
#         f"projects/{PROJECT_NAME}/sitesync/state",
#         localSite="local",
#         remoteSite="remote",
#     )
#     assert response
#     state_row = response["representations"][0]
#     assert state_row["localStatus"]["status"] == 0
#
#     response = api.get(
#         f"projects/{PROJECT_NAME}/sitesync/state",
#         localSite="local",
#         remoteSite="remote",
#         representationId=representation_id,
#     )
#     assert response
#     assert len(response["representations"]) == 1
#     state_row = response["representations"][0]
#
#     assert type(state_row["files"]) is list
#     assert len(state_row["files"]) == 1
