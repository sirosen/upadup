import pytest
from upadup.config import BadConfigError, Config


def test_empty_config_is_valid_and_defines_no_repos():
    c = Config({})
    assert isinstance(c, Config)

    assert c.repos == ()


def test_malformed_repos_is_rejected():
    with pytest.raises(BadConfigError, match=r"'\$\.repos' should be a list"):
        Config({"repos": "foo"})


def test_malformed_extends_default_is_rejected():
    with pytest.raises(
        BadConfigError, match=r"'\$\.extends_default' should be a boolean"
    ):
        Config({"extends_default": "foo"})


def test_repo_config_must_be_map():
    with pytest.raises(BadConfigError, match=r"'\$\.repos\[0\]' should be a map"):
        Config({"repos": ["foo"]})


@pytest.mark.parametrize("ispresent", (True, False))
def test_repo_config_repo_url_must_be_string(ispresent):
    repo_config = {}
    if ispresent:
        repo_config["repo"] = {}
    with pytest.raises(
        BadConfigError, match=r"'\$\.repos\[0\].repo' should be a string"
    ):
        Config({"repos": [repo_config]})


@pytest.mark.parametrize("ispresent", (True, False))
def test_repo_config_repo_hooks_must_be_list(ispresent):
    repo_config = {
        "repo": "snork",
    }
    if ispresent:
        repo_config["hooks"] = "frob"
    with pytest.raises(
        BadConfigError, match=r"'\$\.repos\[0\].hooks' should be a list"
    ):
        Config({"repos": [repo_config]})


def test_repo_config_hooks_items_must_be_maps():
    with pytest.raises(
        BadConfigError, match=r"'\$\.repos\[0\].hooks\[0\]' should be a map"
    ):
        Config({"repos": [{"repo": "snork", "hooks": ["frob"]}]})


@pytest.mark.parametrize("ispresent", (True, False))
def test_repo_config_hook_id_must_be_str(ispresent):
    hook_config = {}
    if ispresent:
        hook_config["id"] = []
    repo_config = {"repo": "snork", "hooks": [hook_config]}
    with pytest.raises(
        BadConfigError, match=r"'\$\.repos\[0\].hooks\[0\].id' should be a string"
    ):
        Config({"repos": [repo_config]})


def test_config_extend_can_add_repos():
    c = Config({})
    assert c.repos == ()

    c.extend(
        {
            "repos": [
                {
                    "repo": "foo",
                    "hooks": [
                        {"id": "bar"},
                    ],
                },
            ]
        }
    )

    assert c.repos == ("foo",)
    assert c.get_hooks("foo") == frozenset(("bar",))
