import pytest

import semanticversioning


@pytest.mark.parametrize(
    "version, expected",
    [
        ("1.2.3", {"major": 1, "minor": 2, "patch": 3}),
        ("1.2", {"major": 1, "minor": 2, "patch": 0}),
        ("1", {"major": 1, "minor": 0, "patch": 0}),
    ],
)
def test_version_from_string(version, expected):
    version = semanticversioning.Version(version)
    assert version.major == expected["major"]
    assert version.minor == expected["minor"]
    assert version.patch == expected["patch"]


@pytest.mark.parametrize(
    "version, expected",
    [
        ([1, 2, 3], {"major": 1, "minor": 2, "patch": 3}),
        ((1, 2), {"major": 1, "minor": 2, "patch": 0}),
        ([1], {"major": 1, "minor": 0, "patch": 0}),
        ((), {"major": 0, "minor": 1, "patch": 0}),
    ],
)
def test_version_from_iterable(version, expected):
    version = semanticversioning.Version(version)
    assert version.major == expected["major"]
    assert version.minor == expected["minor"]
    assert version.patch == expected["patch"]


@pytest.mark.parametrize(
    "version, expected",
    [
        (1, {"major": 1, "minor": 0, "patch": 0}),
        (0, {"major": 0, "minor": 1, "patch": 0}),
    ],
)
def test_version_from_integer(version, expected):
    version = semanticversioning.Version(version)
    assert version.major == expected["major"]
    assert version.minor == expected["minor"]
    assert version.patch == expected["patch"]


@pytest.mark.parametrize(
    "version, expected",
    [
        ({"major": 1, "minor": 2, "patch": 3}, {"major": 1, "minor": 2, "patch": 3}),
        (
            {"major": 1, "patch": 3, "foo": 8, "bar": None},
            {"major": 1, "minor": 0, "patch": 3},
        ),
        ({"minor": 2}, {"major": 0, "minor": 2, "patch": 0}),
        ({}, {"major": 0, "minor": 1, "patch": 0}),
    ],
)
def test_version_from_dictionary(version, expected):
    version = semanticversioning.Version(version)
    assert version.major == expected["major"]
    assert version.minor == expected["minor"]
    assert version.patch == expected["patch"]


@pytest.mark.parametrize(
    "version_a, version_b, expected",
    [
        (
            "1.2.3",
            "4.5",
            {
                "lt": True,
                "lte": True,
                "eq": False,
                "neq": True,
                "gt": False,
                "gte": False,
            },
        ),
        (
            "1.2.3",
            "1.2.3",
            {
                "lt": False,
                "lte": True,
                "eq": True,
                "neq": False,
                "gt": False,
                "gte": True,
            },
        ),
        (
            "1.2",
            "1",
            {
                "lt": False,
                "lte": False,
                "eq": False,
                "neq": True,
                "gt": True,
                "gte": True,
            },
        ),
    ],
)
def test_version_comparison(version_a, version_b, expected):
    version_a = semanticversioning.Version(version_a)
    assert (version_a < version_b) is expected["lt"]
    assert (version_a <= version_b) is expected["lte"]
    assert (version_a == version_b) is expected["eq"]
    assert (version_a != version_b) is expected["neq"]
    assert (version_a > version_b) is expected["gt"]
    assert (version_a >= version_b) is expected["gte"]

    version_b = semanticversioning.Version(version_b)
    assert (version_a < version_b) is expected["lt"]
    assert (version_a <= version_b) is expected["lte"]
    assert (version_a == version_b) is expected["eq"]
    assert (version_a != version_b) is expected["neq"]
    assert (version_a > version_b) is expected["gt"]
    assert (version_a >= version_b) is expected["gte"]


def test_version_bump():
    version = semanticversioning.Version("1.2.3")
    assert version.bump_major() == "2.0.0"
    assert version.bump_minor() == "1.3.0"
    assert version.bump_patch() == "1.2.4"
    assert version.bump_major().bump_minor().bump_patch() == "2.1.1"


@pytest.mark.parametrize(
    "version_a, version_b, expected",
    [
        ("1.2.3", "4.5", -1),
        ("6", "6.0.0", 0),
        ("3.6", "3", 1),
        ("4.5", 3, 1),
        ("0.1", [], 0),
        ("3.3.7", (3, 3, 9), -1),
        ("2", {"patch": 9}, 1),
    ],
)
def test_compare(version_a, version_b, expected):
    assert semanticversioning.compare(version_a, version_b) == expected


def test_max_version():
    versions = ["1.2", 7, (5, 4, 11), {"major": 3, "patch": 10}]
    assert semanticversioning.max_version(versions) == "7.0.0"


def test_min_version():
    versions = ["1.2", 7, (5, 4, 11), {"major": 3, "patch": 10}]
    assert semanticversioning.min_version(versions) == "1.2.0"
