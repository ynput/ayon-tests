from tests.fixtures import api

import hashlib


TEST_PACKAGE = b"FAKEZIP3904095709145 1904jfas dfj90 329jrffm 23e90 fm2390j"
CHECKSUM = hashlib.md5(TEST_PACKAGE).hexdigest()


def test_dependency_packages(api):
    # Create a package
    res = api.put(
        "dependencies",
        name="test_package",
        platform="windows",
        size=len(TEST_PACKAGE),
        checksum=CHECKSUM,
    )

    assert res

    # upload the package
    res = api.raw_post(
        "dependencies/test_package/windows",
        mime="application/octet-stream",
        data=TEST_PACKAGE,
    )
    assert res

    # ensure uploaded package is there
    res = api.raw_get("dependencies/test_package/windows")
    assert res == TEST_PACKAGE


    # ensure it is now listed in sources
    res = api.get("dependencies")
    assert res


    # delete the package
    res = api.delete("dependencies/test_package/windows")
    assert res
