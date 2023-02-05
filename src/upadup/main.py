from __future__ import annotations

import argparse
import collections
import difflib
import os
import pathlib
import sys
import typing as t

from . import config, yaml
from .package_utils import normalize_package_name


def load_precommit_config() -> tuple[dict[str, t.Any], None | str | tuple[str, ...]]:
    path = pathlib.Path.cwd() / ".pre-commit-config.yaml"
    if not path.is_file():
        raise ValueError("upadup cannot run without .pre-commit-config.yaml")

    with path.open() as fp:
        return yaml.load(fp), fp.newlines


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
    for current in hook_config.get("additional_dependencies", ()):
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
    line_offsets: dict[int, int] = collections.defaultdict(int)
    for old_dep, new_dep in updates:
        lineno, column = old_dep.lc.line, old_dep.lc.col

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


def apply_updates(
    config_path: pathlib.Path, updates, newline: None | str | tuple[str, ...]
):
    file_content = create_new_content(config_path, updates)

    # If no newlines were encountered, use the OS default.
    if newline is None:
        newline = os.linesep
    # If multiple newline variants were encountered, pick one.
    # Note that the order of newlines in the tuple is meaningless.
    if isinstance(newline, tuple):
        newline = newline[0]

    with config_path.open("w", newline=newline) as fp:
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

    upadup_config = config.load_upadup_config()
    precommit_config, existing_newlines = load_precommit_config()

    all_updates = []
    for repo_config in precommit_config["repos"]:
        repo_str = repo_config.get("repo").casefold()
        # Strip the ".git" suffix from the repo URL, if present.
        if repo_str.endswith(".git"):
            repo_str = repo_str[:-4]
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
            apply_updates(
                pathlib.Path.cwd() / ".pre-commit-config.yaml",
                all_updates,
                existing_newlines,
            )
            print("done")
    else:
        print("no updates needed in any hook configs")
