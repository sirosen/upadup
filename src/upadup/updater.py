from __future__ import annotations

import collections
import difflib
import functools
import pathlib
import sys
import typing as t

from . import config, yaml
from .providers import github, pypi


def _load_precommit_config(path: pathlib.Path) -> dict[str, t.Any]:
    if not path.is_file():
        raise ValueError("upadup cannot run without .pre-commit-config.yaml")

    return yaml.load(path.read_bytes().decode())


class UpdateCollection:
    def __init__(self) -> None:
        self._data: list[tuple[yaml.StrWithLoc, str]] = []

    def add(self, original: yaml.StrWithLoc, new: str) -> None:
        self._data.append((original, new))

    def extend(self, additions: t.Iterable[tuple[yaml.StrWithLoc, str]]) -> None:
        self._data.extend(additions)

    def sort(self) -> None:
        """sort data in place"""
        self._data = sorted(self._data, key=_sort_updates_key)

    def __iter__(self) -> t.Iterator[tuple[yaml.StrWithLoc, str]]:
        yield from self._data

    def __bool__(self) -> bool:
        return bool(self._data)


def _sort_updates_key(update):
    current_dependency, new_dependency = update
    return (current_dependency.lc.line, current_dependency.lc.col)


class UpadupUpdater:
    def __init__(self, path: pathlib.Path | None = None, freeze: bool = False) -> None:
        self.freeze = freeze
        self.path = path or (pathlib.Path.cwd() / ".pre-commit-config.yaml")
        self._updates = UpdateCollection()

        precommit_config = _load_precommit_config(self.path)
        self._precommit_config = precommit_config

        self._version_map = pypi.VersionMap()

    @functools.cached_property
    def _upadup_config(self) -> config.Config:
        return config.Config.load()

    def has_updates(self) -> bool:
        return bool(self._updates)

    def render_diff(self) -> str:
        old_content, new_content = _create_new_content(self.path, self._updates)
        return "".join(
            difflib.unified_diff(
                old_content,
                new_content,
                self.path.name,
                self.path.name,
            )
        )

    def apply_updates(self) -> None:
        _, new_content = _create_new_content(self.path, self._updates)

        # write the data as UTF-8 bytes, to ensure that `\r\n` is not turned into
        # `\r\r\n` on Windows, where `os.linesep` is `\r\n`
        self.path.write_bytes("".join(new_content).encode())

    def run(self) -> UpdateCollection:
        for precommit_repo_config in self._precommit_config["repos"]:
            if precommit_repo_config["repo"] in self._upadup_config.skip_repos:
                continue

            for hook_config in precommit_repo_config["hooks"]:
                if not hook_config.get("additional_dependencies"):
                    continue
                self._updates.extend(self._generate_hook_updates(hook_config))

        self._updates.sort()
        return self._updates

    def _generate_hook_updates(
        self, hook_config: dict[str, t.Any]
    ) -> t.Iterator[tuple[yaml.StrWithLoc, str]]:
        print(
            f"upadup is checking additional_dependencies of {hook_config['id']}...",
            end="",
        )
        new_deps = self._build_updated_dependency_map(hook_config)
        if new_deps:
            print()
            for current_dependency, new_dependency in new_deps.items():
                print(f"  {current_dependency} => {new_dependency}")
                yield (current_dependency, new_dependency)
        else:
            print("no updates needed")

    def _build_updated_dependency_map(
        self, hook_config: dict[str, t.Any]
    ) -> dict[yaml.StrWithLoc, t.Any]:
        new_deps = {}
        for current in hook_config.get("additional_dependencies", ()):
            new_dependency = self._update_dependency(current)
            if new_dependency == current:
                continue
            new_deps[current] = new_dependency
        return new_deps

    def _update_dependency(self, current_dependency: str) -> str:
        if current_dependency.startswith("github.com/"):
            return github.get_latest_tag(current_dependency, freeze=self.freeze)
        try:
            specifier = pypi.parse_specifier(current_dependency)
        except pypi.UnsupportedSpecifierError:
            return current_dependency
        except pypi.SpecifierParseError:
            print(
                f"'{current_dependency}' did not parse correctly, skipping",
                file=sys.stderr,
            )
            return current_dependency

        new_version = self._version_map[specifier.package_name]
        return specifier.update_version(new_version).format()


def _create_new_content(
    config_path: pathlib.Path, updates: UpdateCollection
) -> tuple[list[str], list[str]]:
    # preserve the original newlines, do not modify them
    with config_path.open("r", newline="", encoding="utf-8") as fp:
        old_content = fp.readlines()
    new_content = old_content.copy()

    # NB: int() == 0
    line_offsets: dict[int, int] = collections.defaultdict(int)
    for old_dep, new_dep in updates:
        lineno, column = old_dep.lc.line, old_dep.lc.col

        begin = column + line_offsets[lineno]
        end = begin + len(old_dep)
        line_offsets[lineno] += len(new_dep) - len(old_dep)

        old_line = new_content[lineno]
        new_content[lineno] = "".join((old_line[:begin], new_dep, old_line[end:]))

    return old_content, new_content
