from __future__ import annotations

import pathlib
import typing as t

from . import yaml
from .package_utils import get_pkg_latest, normalize_package_name


class BadConfigError(ValueError):
    def __init__(self, message: str) -> None:
        super().__init__(f"malformed config: {message}")


DEFAULT_CONFIG = yaml.load(
    """\
repos:
  - repo: https://github.com/pycqa/flake8
    hooks:
      - id: flake8
        additional_dependencies:
          - flake8-bandit
          - flake8-bugbear
          - flake8-builtins
          - flake8-comprehensions
          - flake8-docstrings
          - flake8-implicit-str-concat
          - flake8-logging-format
          - flake8-pyi
          - flake8-typing-as-t
          - flake8-typing-imports

  - repo: https://github.com/adamchainz/blacken-docs
    hooks:
      - id: blacken-docs
        additional_dependencies:
          - black

  # Old hook URLs
  # -------------

  - repo: https://github.com/asottile/blacken-docs
    hooks:
      - id: blacken-docs
        additional_dependencies:
          - black
"""
)


def _read_upadup_config() -> dict[str, t.Any]:
    path = pathlib.Path.cwd() / ".upadup.yaml"
    if not path.is_file():
        return {}
    with path.open() as fp:
        return yaml.load(fp)


def _validate_config(conf_dict: dict[str, t.Any]) -> None:
    if "repos" in conf_dict:
        if not isinstance(conf_dict["repos"], list):
            raise BadConfigError("'$.repos' should be list")
        for i_repo, repo_config in enumerate(conf_dict["repos"]):
            if not isinstance(repo_config, dict):
                raise BadConfigError(f"'$.repos[{i_repo}]' should be map")
            if not isinstance(repo_config.get("repo"), str):
                raise BadConfigError(f"'$.repos[{i_repo}].repo' should be string")
            if not isinstance(repo_config.get("hooks"), list):
                raise BadConfigError(f"'$.repos[{i_repo}].hooks' should be list")
            for i_hook, hook_config in enumerate(repo_config["hooks"]):
                if not isinstance(hook_config["id"], str):
                    raise BadConfigError(
                        f"'$.repos[{i_repo}].hooks[{i_hook}].id' should be string"
                    )
                if not isinstance(hook_config.get("additional_dependencies"), list):
                    raise BadConfigError(
                        f"'$.repos[{i_repo}].hooks[{i_hook}].additional_dependencies' "
                        "should be list"
                    )
                for i_ad, dep in enumerate(hook_config["additional_dependencies"]):
                    if not isinstance(dep, str):
                        raise BadConfigError(
                            f"'$.repos[{i_repo}].hooks[{i_hook}]"
                            f".additional_dependencies[{i_ad}]' should be string"
                        )

    if "extends_default" in conf_dict:
        if not isinstance(conf_dict["extends_default"], bool):
            raise ValueError("malformed config, '$.extends_default' should be boolean")


def _populate_map(
    conf_map: dict[str, t.Any], full_config: dict[str, t.Any], versions: dict[str, str]
) -> None:
    for repo_config in full_config.get("repos", []):
        repo_str = repo_config["repo"].casefold()
        if repo_str not in conf_map:
            conf_map[repo_str] = {}
        for hook_config in repo_config["hooks"]:
            hook_id = hook_config["id"]
            additional_dependencies = hook_config["additional_dependencies"]

            for dep in [normalize_package_name(n) for n in additional_dependencies]:
                if dep not in versions:
                    versions[dep] = get_pkg_latest(dep)

            if hook_id not in conf_map[repo_str]:
                conf_map[repo_str][hook_id] = additional_dependencies
            else:
                conf_map[repo_str][hook_id].extend(additional_dependencies)


def load_upadup_config() -> dict[str, t.Any]:
    upadup_config = _read_upadup_config()
    _validate_config(upadup_config)

    versions: dict[str, str] = {}
    upadup_config_map: dict[str, t.Any] = {}

    if upadup_config.get("extends_default", True):
        _populate_map(upadup_config_map, DEFAULT_CONFIG, versions)
    _populate_map(upadup_config_map, upadup_config, versions)

    return {"repos": upadup_config_map, "versions": versions}
