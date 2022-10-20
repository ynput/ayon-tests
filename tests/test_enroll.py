import pytest
from tests.fixtures import api, PROJECT_NAME


def test_enroll(api):
    res = api.post(
        "events",
        topic="test.source",
        sender="myself",
    )
    assert res

    source_id = res.data["id"]

    res = api.patch(
        f"events/{source_id}",
        description="Hello",
    )
    assert res

    # res = api.post(
    #     "enroll",
    #     sourceTopic="test.source",
    #     targetTopic="test.target",
    #     sender="myself",
    #
    # )
    #
