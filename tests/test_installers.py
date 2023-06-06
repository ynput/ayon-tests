from tests.fixtures import api

import hashlib


TEST_PACKAGE = b"FAKEZIP3904095709145 1904jfas dfj90 329jrffm 23e90 fm2390j"
CHECKSUM = hashlib.md5(TEST_PACKAGE).hexdigest()
FILENAME = "test-package-9.7.4.zip"


def test_installer(api):
    # Create installer
    res = api.post(
        "desktop/installers",
        version="9.7.4",
        platform="windows",
        filename=FILENAME,
        pythonVersion="3.7",
        pythonModules={"numpy": "1.2.3"},
    )

    assert res

    res = api.get("desktop/installers")
    assert res

    for installer in res.data:
        if installer["version"] != "9.7.4":
            continue
        if installer["platform"] != "windows":
            continue
        if installer["pythonVersion"] != "3.7":
            continue
        if installer["pythonModules"] != {"numpy": "1.2.3"}:
            continue
        break
    else:
        assert False, "Installer not found"

    # Upload the package

    res = api.raw_put(
        f"desktop/installers/9.7.4/{FILENAME}",
        mime="application/octet-stream",
        data=TEST_PACKAGE,
    )

    assert res

    # Check the test-package-9

    res = api.raw_get(f"desktop/installers/9.7.4/{FILENAME}")
    assert res == TEST_PACKAGE

    # delete the package

    res = api.delete(f"desktop/installers/9.7.4/{FILENAME}")
    assert res

    # Check the test-package-9

    res = api.raw_get(f"desktop/installers/9.7.4/{FILENAME}")
    assert res != TEST_PACKAGE
