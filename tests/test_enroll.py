import pytest
from tests.fixtures import api as admin_api
from client.api import API


USER_NAME = "testserviceuser"
API_KEY = "boob" * 8


@pytest.fixture
def service_user(admin_api):
    admin_api.delete(f"users/{USER_NAME}")

    res = admin_api.post(
        "eventops",
        type="delete",
        filter={
            "conditions": [
                {
                    "key": "topic",
                    "operator": "like",
                    "value": "test.%",
                }
            ]
        },
    )
    assert res, f"Failed to delete events: {res}"

    data = admin_api.gql(
        'query MyQuery{events(topics:["test.*"]){ edges { node { id } } }}'
    )
    assert data, f"Failed to get events: {data}"
    for event in data["events"]["edges"]:
        admin_api.delete(f"events/{event['node']['id']}")

    res = admin_api.put(f"users/{USER_NAME}", apiKey=API_KEY, data={"isService": True})
    assert res, f"Failed to create service user: {res}"

    api = API(server_url=admin_api.server_url, api_key=API_KEY)

    yield api

    # data = admin_api.gql('query MyQuery{events(topics:["test.*"]){ edges { node { id } } }}')
    # assert data, f"Failed to get events: {data}"
    # for event in data["events"]["edges"]:
    #     admin_api.delete(f"events/{event['node']['id']}")
    #
    admin_api.delete(f"/users/{USER_NAME}")


def test_enroll(service_user):
    res = service_user.post(
        "events",
        topic="test.source.one",
        sender="myself",
    )
    assert res

    source_one_id = res.data["id"]

    res = service_user.post(
        "events",
        topic="test.source.two",
        sender="myself",
    )
    assert res

    source_two_id = res.data["id"]

    res = service_user.post(
        "enroll",
        sourceTopic="test.source.one",
        targetTopic="test.target.one",
        sender="myself",
    )

    assert res
    assert res.data["dependsOn"] in [
        source_one_id,
        source_two_id,
    ], "dependsOn should be source_one_id"
    target_one_id = res.data["id"]

    res = service_user.patch(
        f"events/{target_one_id}",
        status="finished",
    )

    # Test multiple enrollments

    expected_deps = set([source_one_id, source_two_id])
    actual_deps = set()

    while True:
        res = service_user.post(
            "enroll",
            sourceTopic=["test.source.one", "test.source.two"],
            targetTopic="test.target.two",
            sender="myself",
        )

        assert res
        if not res.data:
            break

        target_event_id = res.data["id"]
        service_user.patch(
            f"events/{target_event_id}",
            status="finished",
        )

        actual_deps.add(res.data["dependsOn"])

    assert (
        actual_deps == expected_deps
    ), "Actual dependencies should match expected dependencies"
