import subprocess
import textwrap

import pytest

import upadup.providers.github.cli


@pytest.fixture(autouse=True)
def reset_gh_cli_availability():
    yield
    upadup.providers.github.cli.HAS_CLI = None


@pytest.mark.parametrize("available", (True, False))
def test_gh_cli_availability_is_known(monkeypatch, available):
    """If the GitHub CLI availability is known, subsequent checks must be no-ops."""

    def raiser(*_, **__):
        raise LookupError("shutil.which should not have been called.")

    monkeypatch.setattr("upadup.providers.github.cli.shutil.which", raiser)
    monkeypatch.setattr("upadup.providers.github.cli.HAS_CLI", available)

    assert upadup.providers.github.cli.has_cli() is available


def test_gh_cli_not_on_path(monkeypatch):
    """If shutil.which() cannot find 'gh', the GitHub CLI must be unavailable."""

    monkeypatch.setattr("upadup.providers.github.cli.shutil.which", lambda *_: None)

    assert upadup.providers.github.cli.has_cli() is False
    assert upadup.providers.github.cli.HAS_CLI is False, "result not cached"


def test_gh_cli_is_logged_in(monkeypatch):
    """If the GitHub CLI is available and logged in, has_cli() should return True."""

    stdout = """\
    github.com
      ✓ Logged in to github.com account bogus (keyring)
      - Active account: true
      - Git operations protocol: ssh
      - Token: gho_************************************
      - Token scopes: 'admin:public_key', 'gist', 'read:org', 'repo'
    """
    stdout = textwrap.dedent(stdout)

    def subprocess_runner(*args, **kwargs):
        run_args = kwargs.get("args", None) or args[0]
        return subprocess.CompletedProcess(run_args, returncode=0, stdout=stdout)

    monkeypatch.setattr("upadup.providers.github.cli.shutil.which", lambda *_: "gh")
    monkeypatch.setattr("upadup.providers.github.cli.subprocess.run", subprocess_runner)

    assert upadup.providers.github.cli.has_cli() is True
    assert upadup.providers.github.cli.HAS_CLI is True, "result not cached"


def test_gh_cli_is_not_logged_in(monkeypatch):
    """If the GitHub CLI is available but not logged in, has_cli() must return False."""

    stderr = "You are not logged into any GitHub hosts. To log in, run: gh auth login"

    def subprocess_runner(*args, **kwargs):
        run_args = kwargs.get("args", None) or args[0]
        return subprocess.CompletedProcess(run_args, returncode=1, stderr=stderr)

    monkeypatch.setattr("upadup.providers.github.cli.shutil.which", lambda *_: "gh")
    monkeypatch.setattr("upadup.providers.github.cli.subprocess.run", subprocess_runner)

    assert upadup.providers.github.cli.has_cli() is False
    assert upadup.providers.github.cli.HAS_CLI is False, "result not cached"


def test_gh_cli_get_tags(monkeypatch):
    """Verify that GitHub CLI invocations to get tags are loaded as JSON."""

    def subprocess_runner(*args, **kwargs):
        run_args = kwargs.get("args", None) or args[0]
        return subprocess.CompletedProcess(run_args, returncode=0, stdout="[]")

    monkeypatch.setattr("upadup.providers.github.cli.subprocess.run", subprocess_runner)

    assert isinstance(upadup.providers.github.cli.get_tags_json("org", "repo"), list)
