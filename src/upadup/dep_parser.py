from __future__ import annotations

import dataclasses
import re
import typing as t


class UnsupportedSpecifierError(ValueError):
    def __init__(self, specifier: str) -> None:
        self.specifier = specifier
        super().__init__(f"Specifier did not match a supported format: {specifier}")


class SpecifierParseError(ValueError):
    def __init__(self, specifier: str) -> None:
        self.specifier = specifier
        super().__init__(f"Could not parse specifier: {specifier}")


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
    if "==" not in specifier or "===" in specifier:
        raise UnsupportedSpecifierError(specifier)

    package_name, _, version = specifier.partition("==")
    try:
        leading_whitespace, package_name, before_comparator_whitespace = (
            _split_off_leading_and_trailing_whitespace(package_name)
        )
    except ValueError as e:
        raise SpecifierParseError(specifier) from e

    try:
        after_comparator_whitespace, version, trailing_whitespace = (
            _split_off_leading_and_trailing_whitespace(version)
        )
    except ValueError as e:
        raise SpecifierParseError(specifier) from e

    return ParsedSpecifier(
        leading_whitespace=leading_whitespace,
        package_name=package_name,
        before_comparator_whitespace=before_comparator_whitespace,
        comparator="==",
        after_comparator_whitespace=after_comparator_whitespace,
        version=version,
        trailing_whitespace=trailing_whitespace,
    )


_WS_PATTERN = re.compile(r"(\s*)(\S*)(\s*)")


def _split_off_leading_and_trailing_whitespace(original: str) -> tuple[str, str, str]:
    match = _WS_PATTERN.match(original)
    if match is None or len(match.group(0)) != len(original):
        raise ValueError(
            f"whitespace matching on '{original}' failed on unexpected spaces"
        )
    return match.group(1, 2, 3)  # type: ignore[return-value]
