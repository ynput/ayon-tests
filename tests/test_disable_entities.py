import time
import pytest
from tests.fixtures import api, PROJECT_NAME

from .test_entities import (
    patch_and_get,
    folder_ids,
    product_id,
    version_id,
    representation_id,
    task_id,
)


def test_folder(api, folder_ids):
    folder_id = folder_ids[1]
    result = patch_and_get(
        api,
        f"projects/{PROJECT_NAME}/folders/{folder_id}",
        active=False,
    )
    assert result["active"] == False


def test_product(api, product_id):
    result = patch_and_get(
        api,
        f"projects/{PROJECT_NAME}/products/{product_id}",
        active=False,
    )
    assert result["active"] == False


def test_version(api, version_id):
    result = patch_and_get(
        api,
        f"projects/{PROJECT_NAME}/versions/{version_id}",
        active=False,
    )
    assert result["active"] == False


def test_representation(api, representation_id):
    result = patch_and_get(
        api,
        f"projects/{PROJECT_NAME}/representations/{representation_id}",
        active=False,
    )
    assert result["active"] == False


def test_task(api, task_id):
    result = patch_and_get(
        api,
        f"projects/{PROJECT_NAME}/tasks/{task_id}",
        active=False,
    )
    assert result["active"] == False
