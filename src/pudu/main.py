from __future__ import annotations

import argparse
import json
import pathlib
import sys
import typing as t
import urllib.request

from . import yaml

DEFAULT_CONFIG = yaml.load(
    """\
repos:
  - repo: https://github.com/pycqa/flake
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


def read_pudu_config() -> dict[str, t.Any]:
    path = pathlib.Path.cwd() / ".pudu.yaml"
    if not path.is_file():
        return DEFAULT_CONFIG

    with path.open() as fp:
        return yaml.load(fp)


def load_pudu_config() -> dict:
    pudu_config = read_pudu_config()

    versions = {}
    pudu_config_map = {}
    for repo_config in pudu_config["repos"]:
        repo_str = repo_config["repo"].casefold()
        pudu_config_map[repo_str] = {}
        for hook_config in repo_config["hooks"]:
            hook_id = hook_config["id"]
            additional_dependencies = hook_config["additional_dependencies"]

            for dep in [normalize_package_name(n) for n in additional_dependencies]:
                if dep not in versions:
                    versions[dep] = get_pkg_latest(dep)

            pudu_config_map[repo_str][hook_id] = additional_dependencies

    return {"repos": pudu_config_map, "versions": versions}


def load_precommit_config() -> dict[str, t.Any]:
    path = pathlib.Path.cwd() / ".pre-commit-config.yaml"
    if not path.is_file():
        raise ValueError("pudu cannot run without .pre-commit-config.yaml")

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


def generate_updates(hook_config, additional_dependencies, dependency_versions):
    print(f"pudu is checking additional_dependencies of {hook_config['id']}...", end="")
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


def apply_updates(config_path: pathlib.Path, updates):
    with config_path.open("r") as fp:
        file_content = fp.readlines()
    for old_dep, new_dep in updates:
        lineno, column = old_dep.lc.line, old_dep.lc.col + 1
        old_line = file_content[lineno]
        file_content[lineno] = "".join(
            (old_line[:column], new_dep, old_line[column + len(old_dep) :])
        )
    with config_path.open("w") as fp:
        fp.write("".join(file_content))


def main(args: list[str] | None = None):
    parser = argparse.ArgumentParser(
        description="pudu -- the pre-commit additional_dependencies updater"
    )
    parser.parse_args(args or sys.argv[1:])

    pudu_config = load_pudu_config()
    precommit_config = load_precommit_config()

    all_updates = []
    for repo_config in precommit_config["repos"]:
        repo_str = repo_config.get("repo").casefold()
        if repo_str in pudu_config["repos"]:
            pudu_repo_config = pudu_config["repos"][repo_str]
            for hook_config in repo_config["hooks"]:
                hook_id = hook_config["id"]
                if hook_id in pudu_repo_config:
                    all_updates.extend(
                        generate_updates(
                            hook_config,
                            pudu_repo_config.get(hook_id, []),
                            pudu_config["versions"],
                        )
                    )

    if all_updates:
        print("apply updates...", end="")
        apply_updates(pathlib.Path.cwd() / ".pre-commit-config.yaml", all_updates)
        print("done")
    else:
        print("no updates needed in any hook configs")
