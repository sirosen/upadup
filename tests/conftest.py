import typing as t

import pytest
import responses


@pytest.fixture(autouse=True)
def mocked_responses():
    responses.start()

    yield

    responses.stop()
    responses.reset()


@pytest.fixture
def mock_package_latest_version(mocked_responses):
    def func(pkg, version):
        responses.get(
            f"https://pypi.python.org/pypi/{pkg}/json",
            json={"info": {"version": version}},
        )

    return func


@pytest.fixture
def mock_github_tags(
    monkeypatch,
) -> t.Iterator[t.Callable[[list[dict[str, str]]], None]]:
    """Mock getting tags from GitHub.

    Simply adding this fixture to a test function signature
    will mock a single tag from the 'wasilibs/go-shellcheck' repo.

    However, the fixture can also be called with a new list of tags to return.
    """

    base = "https://api.github.com/repos/wasilibs/go-shellcheck"
    value = [
        {
            "name": "v0.11.1",
            "zipball_url": f"{base}/zipball/refs/tags/v0.11.1",
            "tarball_url": f"{base}/tarball/refs/tags/v0.11.1",
            "commit": {
                "sha": "4e7020840c303923eb1ab846fc446d77be892570",
                "url": f"{base}/commits/4e7020840c303923eb1ab846fc446d77be892570",
            },
            "node_id": "REF_kwDONR_g3bFyZWZzL3RhZ3MvdjAuMTEuMQ",
        },
    ]

    def setter(tags: list[dict[str, str]]) -> None:
        nonlocal value
        value = tags

    monkeypatch.setattr("upadup.providers.github.api.get_tags_json", lambda *_: value)
    monkeypatch.setattr("upadup.providers.github.cli.get_tags_json", lambda *_: value)
    monkeypatch.setattr("upadup.providers.github.cli.HAS_CLI", True)

    yield setter
