import time
from tests.fixtures import api

import hashlib


TEST_PACKAGE = b"FAKEZIP3904095709145 1904jfas dfj90 329jrffm 23e90 fm2390j"
CHECKSUM = hashlib.md5(TEST_PACKAGE).hexdigest()
FILENAME = "test-package-9.7.4.zip"


def test_bundles(api):
    api.delete("bundles/test-bundle")

    bundle_data = {
        "name": "test-bundle",
        "installerVersion": "9.7.4",
        "addons": {"addon1": "1.0.0", "addon2": "2.0.0", "addon3": "3.0.0"},
        "dependencyPackages": {
            "windows": "winpkg.zip",
        },
    }

    api.post("bundles", **bundle_data)

    def get_bundle():
        bundle_list = api.get("bundles").data.get("bundles")
        for bundle in bundle_list:
            print(bundle)
            if bundle["name"] == "test-bundle":
                return bundle
        else:
            raise Exception("Bundle not found")

    bundle = get_bundle()
    assert bundle["name"] == "test-bundle"
    assert bundle["installerVersion"] == "9.7.4"
    assert bundle["dependencyPackages"].get("windows") == "winpkg.zip"
    assert bundle["dependencyPackages"].get("linux") is None
    assert bundle["dependencyPackages"].get("darwin") is None

    res = api.patch(
        "bundles/test-bundle",
        dependencyPackages={"linux": "linuxpkg.zip", "windows": None},
    )

    assert res

    bundle = get_bundle()

    assert bundle["dependencyPackages"].get("windows") is None
    assert bundle["dependencyPackages"].get("linux") == "linuxpkg.zip"
