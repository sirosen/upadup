import pytest
from upadup.package_utils import normalize_package_name


@pytest.mark.parametrize(
    "package_name, normed_name",
    (
        ("foo", "foo"),
        ("foo_bar", "foo-bar"),
        ("FOO-BAR", "foo-bar"),
    ),
)
def test_normalize_package_name(package_name, normed_name):
    assert normalize_package_name(package_name) == normed_name
