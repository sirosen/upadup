import pytest

import upadup.providers.github


def test_get_latest_tag_api(mock_github_tags, monkeypatch):
    base = "github.com/wasilibs/go-shellcheck/cmd/shellcheck"
    given = f"{base}@v0.0.0"
    expected = f"{base}@v0.11.1"

    # Force use of the API.
    monkeypatch.setattr("upadup.providers.github.cli.HAS_CLI", False)

    assert upadup.providers.github.get_latest_tag(given) == expected


def test_get_latest_tag_cli(mock_github_tags):
    base = "github.com/wasilibs/go-shellcheck/cmd/shellcheck"
    given = f"{base}@v0.0.0"
    expected = f"{base}@v0.11.1"

    assert upadup.providers.github.get_latest_tag(given) == expected


def test_get_latest_tag_frozen(mock_github_tags):
    base = "github.com/wasilibs/go-shellcheck/cmd/shellcheck"
    given = f"{base}@v0.0.0"
    expected = f"{base}@4e7020840c303923eb1ab846fc446d77be892570"

    assert upadup.providers.github.get_latest_tag(given, freeze=True) == expected


def test_get_latest_tag_sorting(mock_github_tags):
    """Ensure tags are sorted before the latest is returned."""

    base = "github.com/wasilibs/go-shellcheck/cmd/shellcheck"
    tags = [  # This is a list comprehension.
        {
            "name": version,
            "zipball_url": f"{base}/zipball/refs/tags/{version}",
            "tarball_url": f"{base}/tarball/refs/tags/{version}",
            "commit": {
                "sha": f"{version[1] * 40}",
                "url": f"{base}/commits/{version[1] * 40}",
            },
            "node_id": "REF_kwDONR_g3bFyZWZzL3RhZ3MvdjAuMTEuMA",
        }
        for version in ("v1.1.1", "v3.3.3", "v2.2.2")  # Latest version is sandwiched
    ]
    mock_github_tags(tags)

    given = "github.com/wasilibs/go-shellcheck/cmd/shellcheck@v0.0.0"
    expected_v = f"{base}@v3.3.3"
    expected_sha = f"{base}@{'3' * 40}"
    assert upadup.providers.github.get_latest_tag(given, freeze=False) == expected_v
    assert upadup.providers.github.get_latest_tag(given, freeze=True) == expected_sha


def test_get_latest_tag_non_github(mock_github_tags):
    given = "gitlab.com/org/repo/subpath@ref"

    with pytest.raises(ValueError, match="Not a GitHub-based dependency"):
        assert upadup.providers.github.get_latest_tag(given, freeze=True)


@pytest.mark.parametrize("freeze", (True, False))
def test_get_latest_tag_no_releases(mock_github_tags, freeze):
    """If there are no releases, what's given should simply be returned."""

    given = "github.com/wasilibs/go-shellcheck/cmd/shellcheck@v0.0.0"
    mock_github_tags([])

    assert upadup.providers.github.get_latest_tag(given, freeze=freeze) == given


@pytest.mark.parametrize("freeze", (True, False))
@pytest.mark.parametrize(
    "version",
    (
        pytest.param("v1.1.1a1", id="pre-release"),
        pytest.param("v1.1.1dev1", id="dev-release"),
        pytest.param("v1.1, plus some extra stuff", id="malformed"),
    ),
)
def test_get_latest_tag_ignore_bad_versions(mock_github_tags, freeze, version):
    """Pre-releases, dev versions, and malformed versions must be ignored.

    Since only one tag is mocked, the expected behavior is that
    no version higher than "0.0.0" will be found,
    and the original dependency line will be returned unchanged.
    """

    base = "https://api.github.com/repos/wasilibs/go-shellcheck"
    tags = [
        {
            "name": version,
            "zipball_url": f"{base}/zipball/refs/tags/{version}",
            "tarball_url": f"{base}/tarball/refs/tags/{version}",
            "commit": {
                "sha": "67a2daf0874f0b66440769a149de31e2423de918",
                "url": f"{base}/commits/67a2daf0874f0b66440769a149de31e2423de918",
            },
            "node_id": "REF_kwDONR_g3bFyZWZzL3RhZ3MvdjAuMTAuMA",
        },
    ]
    mock_github_tags(tags)

    given = "github.com/wasilibs/go-shellcheck/cmd/shellcheck@v0.0.0"

    assert upadup.providers.github.get_latest_tag(given, freeze=freeze) == given
