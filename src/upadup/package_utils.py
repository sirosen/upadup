import typing as t
from collections.abc import Mapping

import requests


def normalize_package_name(name: str) -> str:
    return name.lower().replace("_", "-")


def get_pkg_latest(name: str) -> str:
    version_data = requests.get(f"https://pypi.python.org/pypi/{name}/json", timeout=30)
    return str(version_data.json()["info"]["version"])


class VersionMap(Mapping[str, str]):
    def __init__(self) -> None:
        self._cache: dict[str, str] = {}

    def __getitem__(self, key: str) -> str:
        normed = normalize_package_name(key)
        self._populate(normed)
        return self._cache[normed]

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, str):
            return False
        normed = normalize_package_name(key)
        return normed in self._cache

    def __iter__(self) -> t.Iterator[str]:
        yield from self._cache

    def __len__(self) -> int:
        return len(self._cache)

    def _populate(self, package_name: str) -> None:
        if package_name not in self._cache:
            self._cache[package_name] = get_pkg_latest(package_name)
