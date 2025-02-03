import pytest

from upadup.package_utils import VersionMap, _normalize_package_name


@pytest.mark.parametrize(
    "package_name, normed_name",
    (
        ("foo", "foo"),
        ("foo_bar", "foo-bar"),
        ("foo-bar", "foo-bar"),
        ("foo..-.bar", "foo-bar"),
        ("FOO-BAR", "foo-bar"),
    ),
)
def test_normalize_package_name(package_name, normed_name):
    assert _normalize_package_name(package_name) == normed_name


def test_version_map_lazy_lookup(mock_package_latest_version):
    mock_package_latest_version("click", "3.3.1")

    vmap = VersionMap()

    assert len(vmap) == 0
    assert "click" not in vmap
    assert list(vmap) == []

    assert vmap["click"] == "3.3.1"

    assert len(vmap) == 1
    assert "click" in vmap
    assert list(vmap) == ["click"]


@pytest.mark.parametrize(
    "requested_name, normed_name",
    (
        ("click", "click"),
        ("CLICK", "click"),
        ("click-type-test", "click-type-test"),
        ("click_type_test", "click-type-test"),
        ("Click_Type_Test", "click-type-test"),
    ),
)
def test_version_map_normalizes(
    mock_package_latest_version, requested_name, normed_name
):
    mock_package_latest_version(normed_name, "1.0.1")

    vmap = VersionMap()

    # starts empty
    assert requested_name not in vmap
    assert normed_name not in vmap
    assert len(vmap) == 0
    assert list(vmap) == []

    # denormed request populates with the normed name
    assert vmap[requested_name] == "1.0.1"
    assert len(vmap) == 1
    assert requested_name in vmap
    assert list(vmap) == [normed_name]

    # normed request does not alter contents (but can access data via getitem)
    assert vmap[normed_name] == "1.0.1"
    assert len(vmap) == 1
    assert normed_name in vmap
    assert list(vmap) == [normed_name]
