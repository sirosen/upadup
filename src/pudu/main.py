from __future__ import annotations

import argparse
import json
import pathlib
import sys
import typing as t
import urllib.request

import ruamel.yaml

yaml = ruamel.yaml.YAML(typ="rt")


def normalize_package_name(name: str):
    return name.lower().replace("_", "-")


def get_pkg_latest(name: str) -> str:
    with urllib.request.urlopen(f"https://pypi.python.org/pypi/{name}/json") as conn:
        version_data = json.load(conn)
    return str(version_data["info"]["version"])


def read_pudu_config() -> dict[str, t.Any]:
    path = pathlib.Path.cwd() / ".pudu.yaml"
    if not path.is_file():
        raise ValueError("pudu cannot run without .pudu.yaml")

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
        return current_dependency
    package_name, version = current_dependency.split("==")
    normed_pkg = normalize_package_name(package_name)
    if normed_pkg not in known_dependency_names:
        return current_dependency
    return f"{package_name}=={dependency_versions[normed_pkg]}"


def apply_update(hook_config, additional_dependencies, versions):
    print("update:")
    print(hook_config, additional_dependencies, versions)
    hook_config["additional_dependencies"] = [
        update_dependency(current, additional_dependencies, versions)
        for current in hook_config["additional_dependencies"]
    ]
    print("update done!")


def main(args: list[str] | None = None):
    parser = argparse.ArgumentParser(
        description="pudu -- the pre-commit additional_dependencies updater"
    )
    parser.parse_args(args or sys.argv[1:])

    pudu_config = load_pudu_config()
    precommit_config = load_precommit_config()

    for repo_config in precommit_config["repos"]:
        repo_str = repo_config.get("repo").casefold()
        if repo_str in pudu_config["repos"]:
            pudu_repo_config = pudu_config["repos"][repo_str]
            for hook_config in repo_config["hooks"]:
                hook_id = hook_config["id"]
                if hook_id in pudu_repo_config:
                    apply_update(
                        hook_config,
                        pudu_repo_config.get(hook_id, []),
                        pudu_config["versions"],
                    )

    with (pathlib.Path.cwd() / ".pre-commit-config.yaml").open("w") as fp:
        yaml.dump(precommit_config, fp)
