from __future__ import annotations

import argparse
import collections
import difflib
import json
import pathlib
import sys
import typing as t
import urllib.request

from . import yaml

DEFAULT_CONFIG = yaml.load(
    """\
repos:
  - repo: https://github.com/pycqa/flake8
    hooks:
      - id: flake8
        additional_dependencies:
          - flake8-bandit
          - flake8-bugbear
          - flake8-comprehensions
          - flake8-pyi
          - flake8-typing-imports
          - flake8-docstrings
          - flake8-builtins
  - repo: https://github.com/asottile/blacken-docs
    hooks:
      - id: blacken-docs
        additional_dependencies:
          - black
"""
)


def normalize_package_name(name: str):
    return name.lower().replace("_", "-")


def get_pkg_latest(name: str) -> str:
    with urllib.request.urlopen(f"https://pypi.python.org/pypi/{name}/json") as conn:
        version_data = json.load(conn)
    return str(version_data["info"]["version"])


def read_upadup_config() -> dict[str, t.Any]:
    path = pathlib.Path.cwd() / ".upadup.yaml"
    if not path.is_file():
        return DEFAULT_CONFIG

    with path.open() as fp:
        return yaml.load(fp)


def load_upadup_config() -> dict:
    upadup_config = read_upadup_config()

    versions = {}
    upadup_config_map = {}
    for repo_config in upadup_config["repos"]:
        repo_str = repo_config["repo"].casefold()
        upadup_config_map[repo_str] = {}
        for hook_config in repo_config["hooks"]:
            hook_id = hook_config["id"]
            additional_dependencies = hook_config["additional_dependencies"]

            for dep in [normalize_package_name(n) for n in additional_dependencies]:
                if dep not in versions:
                    versions[dep] = get_pkg_latest(dep)

            upadup_config_map[repo_str][hook_id] = additional_dependencies

    return {"repos": upadup_config_map, "versions": versions}


def load_precommit_config() -> dict[str, t.Any]:
    path = pathlib.Path.cwd() / ".pre-commit-config.yaml"
    if not path.is_file():
        raise ValueError("upadup cannot run without .pre-commit-config.yaml")

    with path.open() as fp:
        return yaml.load(fp)


def update_dependency(current_dependency, known_dependency_names, dependency_versions):
    if "==" not in current_dependency:
        return None

    package_name, _, old_version = current_dependency.partition("==")

    normed_pkg = normalize_package_name(package_name)
    if normed_pkg not in known_dependency_names:
        return None

    new_version = dependency_versions[normed_pkg]
    if old_version == new_version:
        return None

    return f"{package_name}=={dependency_versions[normed_pkg]}"


def build_updated_dependency_map(
    hook_config, known_dependency_names, dependency_versions
):
    new_deps = {}
    for current in hook_config["additional_dependencies"]:
        new_dependency = update_dependency(
            current, known_dependency_names, dependency_versions
        )
        if new_dependency is None:
            continue
        new_deps[current] = new_dependency
    return new_deps


def _sort_updates_key(update):
    current_dependency, new_dependency = update
    return (current_dependency.lc.line, current_dependency.lc.col)


def generate_updates(hook_config, additional_dependencies, dependency_versions):
    print(
        f"upadup is checking additional_dependencies of {hook_config['id']}...", end=""
    )
    new_deps = build_updated_dependency_map(
        hook_config, additional_dependencies, dependency_versions
    )
    if new_deps:
        print()
        for current_dependency, new_dependency in new_deps.items():
            print(f"  {current_dependency} => {new_dependency}")
            yield (current_dependency, new_dependency)
    else:
        print("no updates needed")


def create_new_content(config_path: pathlib.Path, updates):
    with config_path.open("r") as fp:
        file_content = fp.readlines()

    # NB: int() == 0
    line_offsets = collections.defaultdict(int)
    for old_dep, new_dep in updates:
        lineno, column = old_dep.lc.line, old_dep.lc.col + 1

        begin = column + line_offsets[lineno]
        end = begin + len(old_dep)
        line_offsets[lineno] += len(new_dep) - len(old_dep)

        old_line = file_content[lineno]
        file_content[lineno] = "".join((old_line[:begin], new_dep, old_line[end:]))

    return file_content


def generate_diff(config_path: pathlib.Path, updates):
    new_content = create_new_content(config_path, updates)
    with config_path.open("r") as fp:
        old_content = fp.readlines()
    return difflib.unified_diff(
        old_content, new_content, ".pre-commit-config.yaml", ".pre-commit-config.yaml"
    )


def apply_updates(config_path: pathlib.Path, updates):
    file_content = create_new_content(config_path, updates)
    with config_path.open("w") as fp:
        fp.write("".join(file_content))


def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(
        description="upadup -- the pre-commit additional_dependencies updater"
    )
    parser.add_argument(
        "--check",
        help="check and show diff, but do not update",
        action="store_true",
        default=False,
    )
    args = parser.parse_args(argv or sys.argv[1:])

    upadup_config = load_upadup_config()
    precommit_config = load_precommit_config()

    all_updates = []
    for repo_config in precommit_config["repos"]:
        repo_str = repo_config.get("repo").casefold()
        if repo_str in upadup_config["repos"]:
            upadup_repo_config = upadup_config["repos"][repo_str]
            for hook_config in repo_config["hooks"]:
                hook_id = hook_config["id"]
                if hook_id in upadup_repo_config:
                    all_updates.extend(
                        generate_updates(
                            hook_config,
                            upadup_repo_config.get(hook_id, []),
                            upadup_config["versions"],
                        )
                    )

    all_updates = sorted(all_updates, key=_sort_updates_key)

    if all_updates:
        if args.check:
            print(
                "".join(
                    generate_diff(
                        pathlib.Path.cwd() / ".pre-commit-config.yaml", all_updates
                    )
                )
            )
            sys.exit(1)
        else:
            print("apply updates...", end="")
            apply_updates(pathlib.Path.cwd() / ".pre-commit-config.yaml", all_updates)
            print("done")
    else:
        print("no updates needed in any hook configs")
