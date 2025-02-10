import textwrap

import pytest

from upadup.updater import UpadupUpdater


@pytest.fixture
def update_from_text(tmp_path):
    def _updatefunc(content):
        config_path = tmp_path / ".pre-commit-config.yaml"
        config_path.write_text(textwrap.dedent(content))

        updater = UpadupUpdater(path=config_path)
        updater.run()
        updater.apply_updates()

        return config_path.read_text()

    return _updatefunc
