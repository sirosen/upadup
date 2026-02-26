import pytest

from upadup.providers.pypi.dep_parser import (
    SpecifierParseError,
    UnsupportedSpecifierError,
    parse_specifier,
)


@pytest.mark.parametrize(
    "specifier",
    (
        "xyz===1.0",
        "xyz===   1.0",
        "xyz ~= 2.1-dev0",
        "foo==1",
        "foo == 1.0",
        "foo==2.2 ",
        "  foo==1.1b0",
    ),
)
def test_parse_and_format_roundtrips(specifier):
    parsed = parse_specifier(specifier)
    assert specifier == parsed.format()


@pytest.mark.parametrize(
    "specifier",
    (
        "xyz=1.0",
        "xyz>=1.0",
        "xyz<=1.0",
        "xyz>=1.0,<=1.0",
        "xyz!=1.0",
    ),
)
def test_parse_requires_double_equal(specifier):
    with pytest.raises(UnsupportedSpecifierError):
        parse_specifier(specifier)


@pytest.mark.parametrize(
    "specifier",
    (
        "xyz abc == 1.0",
        "xyz==1.0 2.1",
    ),
)
def test_parse_rejects_specifier_with_invalid_whitespace(specifier):
    with pytest.raises(SpecifierParseError):
        parse_specifier(specifier)


@pytest.mark.parametrize("comparator", ("===", "==", "~="))
def test_parse_and_update_version(comparator):
    spec = parse_specifier(f"foo{comparator}1.0.0")
    spec2 = spec.update_version("1.1.1")
    # unchanged
    assert spec.format() == f"foo{comparator}1.0.0"
    # changed!
    assert spec2.format() == f"foo{comparator}1.1.1"
