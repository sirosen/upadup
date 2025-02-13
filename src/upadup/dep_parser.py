from __future__ import annotations

import dataclasses
import re
import typing as t

# Note: order matters because we will check for these in order
# therefore, `===` should come before `==`
SUPPORTED_VERSION_COMPARATORS: tuple[str, ...] = (
    "===",
    "==",
    "~=",
)
# valid `version` strings under the grammar defined in this spec:
#   https://packaging.python.org/en/latest/specifications/dependency-specifiers/#grammar
VALID_VERSION_PATTERN = re.compile(r"^[a-zA-Z0-9\-_\.\*\+!]+$")
# valid `identifier` strings under that same grammar
VALID_PACKAGE_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_\.\-]*[a-zA-Z0-9]$")
# leading and trailing whitespace on a string which contains no inner whitespace
WHITESPACE_PATTERN = re.compile(r"^(\s*)(\S*)(\s*)$")


class UnsupportedSpecifierError(ValueError):
    def __init__(self, specifier: str) -> None:
        self.specifier = specifier
        super().__init__(f"Specifier did not match a supported format: {specifier}")


class SpecifierParseError(ValueError):
    def __init__(
        self,
        *,
        specifier: str | None = None,
        message: str = "Could not parse specifier.",
    ) -> None:
        self.message = message
        self.specifier = specifier

        msg = message
        if specifier is not None:
            msg = f"{msg} specifier={specifier}"

        super().__init__(msg)


@dataclasses.dataclass
class ParsedSpecifier:
    leading_whitespace: str
    package_name: str
    before_comparator_whitespace: str
    comparator: str
    after_comparator_whitespace: str
    version: str
    trailing_whitespace: str

    def format(self) -> str:
        parts = (
            self.leading_whitespace,
            self.package_name,
            self.before_comparator_whitespace,
            self.comparator,
            self.after_comparator_whitespace,
            self.version,
            self.trailing_whitespace,
        )
        return "".join(parts)

    def update_version(self, new_version: str) -> t.Self:
        return dataclasses.replace(self, version=new_version)


def parse_specifier(specifier: str) -> ParsedSpecifier:
    for comparator in SUPPORTED_VERSION_COMPARATORS:
        if comparator in specifier:
            break
    else:
        raise UnsupportedSpecifierError(specifier)

    package_name, _, version = specifier.partition(comparator)
    try:
        leading_whitespace, package_name, before_comparator_whitespace = (
            _split_off_leading_and_trailing_whitespace(package_name)
        )
    except ValueError as e:
        raise SpecifierParseError(
            specifier=specifier, message="Invalid whitespace in package name."
        ) from e

    try:
        after_comparator_whitespace, version, trailing_whitespace = (
            _split_off_leading_and_trailing_whitespace(version)
        )
    except ValueError as e:
        raise SpecifierParseError(
            specifier=specifier, message="Invalid whitespace in version."
        ) from e

    # validate the resulting content and raise a parse error if invalid
    _validate_parsed_data(specifier, package_name, version)

    return ParsedSpecifier(
        leading_whitespace=leading_whitespace,
        package_name=package_name,
        before_comparator_whitespace=before_comparator_whitespace,
        comparator=comparator,
        after_comparator_whitespace=after_comparator_whitespace,
        version=version,
        trailing_whitespace=trailing_whitespace,
    )


def _split_off_leading_and_trailing_whitespace(original: str) -> tuple[str, str, str]:
    match = WHITESPACE_PATTERN.match(original)
    if match is None:
        raise ValueError(
            f"whitespace matching on '{original}' failed on unexpected spaces"
        )
    return match.group(1, 2, 3)  # type: ignore[return-value]


def _validate_parsed_data(specifier: str, package_name: str, version: str) -> None:
    if not VALID_PACKAGE_NAME_PATTERN.match(package_name):
        raise SpecifierParseError(specifier=specifier, message="Invalid package name.")
    if not VALID_VERSION_PATTERN.match(version):
        raise SpecifierParseError(
            specifier=specifier, message="Invalid version string."
        )
