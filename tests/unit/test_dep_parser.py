import pytest

from upadup.dep_parser import (
    SpecifierParseError,
    UnsupportedSpecifierError,
    parse_specifier,
)


@pytest.mark.parametrize(
    "specifier",
    (
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
        "x=1.0",
        "x>=1.0",
        "x<=1.0",
        "x>=1.0,<=1.0",
        "x===1.0",
        "x!=1.0",
    ),
)
def test_parse_requires_double_equal(specifier):
    with pytest.raises(UnsupportedSpecifierError):
        parse_specifier(specifier)


@pytest.mark.parametrize(
    "specifier",
    (
        "x y == 1.0",
        "x==1.0 2.1",
    ),
)
def test_parse_rejects_specifier_with_invalid_whitespace(specifier):
    with pytest.raises(SpecifierParseError):
        parse_specifier(specifier)


def test_parse_and_update_version():
    spec = parse_specifier("foo==1.0.0")
    spec2 = spec.update_version("1.1.1")
    # unchanged
    assert spec.format() == "foo==1.0.0"
    # changed!
    assert spec2.format() == "foo==1.1.1"
