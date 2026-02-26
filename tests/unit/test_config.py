import os
import pathlib
import re
from textwrap import dedent as d

import pytest

from upadup.config import BadConfigError, Config


@pytest.fixture
def in_tmp_dir(tmp_path):
    cwd = pathlib.Path.cwd()
    try:
        os.chdir(tmp_path)
        yield tmp_path
    finally:
        os.chdir(cwd)


def test_no_config_is_valid_and_defines_no_skip_repos(in_tmp_dir):
    c = Config.load()
    assert isinstance(c, Config)
    assert c.skip_repos == ()


@pytest.mark.parametrize("config_file_name", [".upadup.toml", "pyproject.toml"])
@pytest.mark.parametrize("file_contents", ["\n", "[tool]\n", "[tool.upadup]\n"])
def test_empty_config_is_valid_and_defines_no_skip_repos(
    in_tmp_dir, config_file_name, file_contents
):
    config_file = in_tmp_dir / config_file_name
    config_file.write_text(file_contents)

    c = Config.load()
    assert isinstance(c, Config)
    assert c.skip_repos == ()


@pytest.mark.parametrize("config_file_name", [".upadup.toml", "pyproject.toml"])
@pytest.mark.parametrize(
    "file_contents, expect_message",
    [
        ("tool = []\n", "'tool' was not a table"),
        ("tool.upadup = []\n", "'tool.upadup' was not a table"),
        ("tool.upadup.skip_repos = 1\n", "'tool.upadup.skip_repos' should be a list"),
        (
            "tool.upadup.skip_repos = ['a', 1]\n",
            "'tool.upadup.skip_repos[1]' was not a string",
        ),
    ],
)
def test_malformed_config_is_rejected(
    in_tmp_dir, config_file_name, file_contents, expect_message
):
    config_file = in_tmp_dir / config_file_name
    config_file.write_text(file_contents)

    with pytest.raises(BadConfigError, match=re.escape(expect_message)):
        Config.load()


@pytest.mark.parametrize("config_file_name", [".upadup.toml", "pyproject.toml"])
@pytest.mark.parametrize(
    "file_contents, expect_skip_repos",
    [
        ("tool.upadup = {skip_repos = ['foo']}\n", ("foo",)),
        (
            d("""\
            [tool.upadup]
            skip_repos = []
            """),
            (),
        ),
        (
            d("""\
            [tool.upadup]
            skip_repos = ['a', 'b', 'c']
            """),
            ("a", "b", "c"),
        ),
    ],
)
def test_config_with_skip_repos_config(
    in_tmp_dir, config_file_name, file_contents, expect_skip_repos
):
    config_file = in_tmp_dir / config_file_name
    config_file.write_text(file_contents)

    c = Config.load()
    assert c.skip_repos == expect_skip_repos
