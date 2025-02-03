import re
import typing as t
from collections.abc import Mapping

import requests

# this normalization pattern follows the rules declared for package normalization
# on pypi itself
# newer build backends are guaranteed to canonicalize the name portion of dist files
# to this form, and other ecosystem components may also rely on this canonical form
_NORMALIZATION_PATTERN = re.compile(r"[-_.]+")


def _normalize_package_name(name: str) -> str:
    return _NORMALIZATION_PATTERN.sub("-", name).lower()


def get_pkg_latest(name: str) -> str:
    version_data = requests.get(f"https://pypi.python.org/pypi/{name}/json", timeout=30)
    return str(version_data.json()["info"]["version"])


class VersionMap(Mapping[str, str]):
    def __init__(self) -> None:
        self._cache: dict[str, str] = {}

    def __getitem__(self, key: str) -> str:
        normed = _normalize_package_name(key)
        self._populate(normed)
        return self._cache[normed]

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, str):
            return False
        normed = _normalize_package_name(key)
        return normed in self._cache

    def __iter__(self) -> t.Iterator[str]:
        yield from self._cache

    def __len__(self) -> int:
        return len(self._cache)

    def _populate(self, package_name: str) -> None:
        if package_name not in self._cache:
            self._cache[package_name] = get_pkg_latest(package_name)
