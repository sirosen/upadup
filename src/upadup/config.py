from __future__ import annotations

import pathlib
import typing as t

from . import yaml


class BadConfigError(ValueError):
    def __init__(self, message: str) -> None:
        super().__init__(f"malformed config: {message}")


class Config:
    def __init__(self, source: str | dict[str, t.Any]) -> None:
        # structure is
        #   { <repo> : { <hook_id> : None } }
        self._data: dict[str, dict[str, None]] = {}
        if isinstance(source, str):
            loaded = yaml.load(source)
            if not isinstance(loaded, dict):
                raise BadConfigError("cannot load a config which is a non-mapping type")
            source = loaded
        self.extend(source)

    def extend(self, other_config: dict[str, t.Any]) -> None:
        _validate_config(other_config)
        for repo_config in other_config.get("repos", []):
            repo_str = repo_config["repo"].casefold()
            self._data.setdefault(repo_str, {})
            for hook_config in repo_config["hooks"]:
                hook_id = hook_config["id"]
                self._data[repo_str].setdefault(hook_id)

    @property
    def repos(self) -> tuple[str, ...]:
        return tuple(self._data)

    def get_hooks(self, repo_name: str) -> frozenset[str]:
        return frozenset(self._data[repo_name])


DEFAULT_CONFIG_DATA = """\
repos:
  - repo: https://github.com/pycqa/flake8
    hooks:
      - id: flake8

  - repo: https://github.com/adamchainz/blacken-docs
    hooks:
      - id: blacken-docs

  # Old hook URLs
  # -------------

  - repo: https://github.com/asottile/blacken-docs
    hooks:
      - id: blacken-docs
"""


def _validate_config(conf_dict: dict[str, t.Any]) -> None:
    if "repos" in conf_dict:
        if not isinstance(conf_dict["repos"], list):
            raise BadConfigError("'$.repos' should be a list")
        for i_repo, repo_config in enumerate(conf_dict["repos"]):
            if not isinstance(repo_config, dict):
                raise BadConfigError(f"'$.repos[{i_repo}]' should be a map")
            if not isinstance(repo_config.get("repo"), str):
                raise BadConfigError(f"'$.repos[{i_repo}].repo' should be a string")
            if not isinstance(repo_config.get("hooks"), list):
                raise BadConfigError(f"'$.repos[{i_repo}].hooks' should be a list")
            for i_hook, hook_config in enumerate(repo_config["hooks"]):
                if not isinstance(hook_config, dict):
                    raise BadConfigError(
                        f"'$.repos[{i_repo}].hooks[{i_hook}]' should be a map"
                    )
                if not isinstance(hook_config.get("id"), str):
                    raise BadConfigError(
                        f"'$.repos[{i_repo}].hooks[{i_hook}].id' should be a string"
                    )

    if "extends_default" in conf_dict:
        if not isinstance(conf_dict["extends_default"], bool):
            raise BadConfigError("'$.extends_default' should be a boolean")


def _read_local_config() -> dict[str, t.Any] | None:
    path = pathlib.Path.cwd() / ".upadup.yaml"
    if not path.is_file():
        return None
    with path.open() as fp:
        return yaml.load(fp)


def load_upadup_config() -> Config:
    local_config = _read_local_config()

    config = Config(DEFAULT_CONFIG_DATA)
    if local_config is not None:
        config.extend(local_config)
    return config
