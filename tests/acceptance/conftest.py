import os
import textwrap

import pytest

from upadup.main import apply_updates, generate_all_updates, load_precommit_config


@pytest.fixture
def _in_tmp_path(tmp_path):
    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    yield
    os.chdir(old_cwd)


@pytest.fixture
def update_from_text(_in_tmp_path, tmp_path):
    def _updatefunc(content):
        config_path = tmp_path / ".pre-commit-config.yaml"
        config_path.write_text(textwrap.dedent(content))

        precommit_config, newlines = load_precommit_config()
        all_updates = generate_all_updates(precommit_config)
        apply_updates(config_path, all_updates, newlines)

        return config_path.read_text()

    return _updatefunc
