from __future__ import annotations

import pathlib
import sys
import typing as t

if sys.version_info < (3, 11):
    from typing_extensions import Self
else:
    from typing import Self

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


class BadConfigError(ValueError):
    def __init__(self, message: str) -> None:
        super().__init__(f"malformed config: {message}")


class Config:
    def __init__(self, skip_repos: t.Iterable[str]) -> None:
        self._skip_repos = tuple(skip_repos)

    @property
    def skip_repos(self) -> tuple[str, ...]:
        return self._skip_repos

    @classmethod
    def _load_dict(cls, data: dict[str, t.Any]) -> Self:
        skip_repos: list[str] = []

        unexpected_keys = list(set(data.keys()) - {"skip_repos"})

        if unexpected_keys:
            raise BadConfigError(
                f"'tool.upadup' contained unexpected keys: {unexpected_keys!r}"
            )

        if "skip_repos" in data:
            skip_repos = data["skip_repos"]
            if not isinstance(skip_repos, list):
                raise BadConfigError("'tool.upadup.skip_repos' should be a list")
            for i, s in enumerate(skip_repos):
                if not isinstance(s, str):
                    raise BadConfigError(
                        f"'tool.upadup.skip_repos[{i}]' was not a string"
                    )

        return cls(skip_repos=skip_repos)

    @classmethod
    def load(cls) -> Self:
        raw_config = _read_raw_config()
        return cls._load_dict(raw_config)


def _read_local_toml_file() -> dict[str, t.Any] | None:
    path = pathlib.Path.cwd() / ".upadup.toml"
    if not path.is_file():
        return None
    with path.open("rb") as fp:
        return tomllib.load(fp)


def _read_pyproject_toml_file() -> dict[str, t.Any] | None:
    path = pathlib.Path.cwd() / "pyproject.toml"
    if not path.is_file():
        return None
    with path.open("rb") as fp:
        return tomllib.load(fp)


def _read_raw_config() -> dict[str, t.Any]:
    data = _read_local_toml_file()
    if data is None:
        data = _read_pyproject_toml_file()
    if data is None:
        return {}

    if "tool" not in data:
        return {}
    tool_table = data["tool"]
    if not isinstance(tool_table, dict):
        raise BadConfigError("'tool' was not a table")
    if "upadup" not in tool_table:
        return {}

    raw_config = tool_table["upadup"]
    if not isinstance(raw_config, dict):
        raise BadConfigError("'tool.upadup' was not a table")
    return raw_config
