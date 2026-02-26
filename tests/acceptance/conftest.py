from __future__ import annotations

import contextlib
import os
import pathlib
import textwrap

import pytest

from upadup.updater import UpadupUpdater


@pytest.fixture
def update_from_text(tmp_path):
    def _updatefunc(
        content: str, config_content: str | None = None, freeze: bool = False
    ):
        precommit_config_path = tmp_path / ".pre-commit-config.yaml"
        precommit_config_path.write_text(textwrap.dedent(content))

        if config_content is not None:
            config_path = tmp_path / ".upadup.toml"
            config_path.write_text(textwrap.dedent(config_content))

        updater = UpadupUpdater(path=precommit_config_path, freeze=freeze)
        with _in_dir(tmp_path):
            updater.run()
            updater.apply_updates()

        return precommit_config_path.read_text()

    return _updatefunc


@contextlib.contextmanager
def _in_dir(path):
    cwd = pathlib.Path.cwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(cwd)
