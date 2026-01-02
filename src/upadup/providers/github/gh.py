import json
import shutil
import subprocess

import packaging.version

HAS_GITHUB_CLI = None


def has_gh() -> bool:
    """Determine if the gh executable is available, and has a valid session active."""

    global HAS_GITHUB_CLI
    if HAS_GITHUB_CLI is not None:
        return HAS_GITHUB_CLI

    if shutil.which("gh") is None:
        HAS_GITHUB_CLI = False
    else:
        stdout = subprocess.check_output("gh auth status".split())
        HAS_GITHUB_CLI = b"logged in to github.com" in stdout.lower()

    return HAS_GITHUB_CLI


def get_tags(owner: str, repo: str) -> dict[packaging.version.Version, dict[str, str]]:
    """Get recent tags for a repo."""

    command = ["gh", "api"]
    command.extend(["-H", "Accept: application/vnd.github+json"])
    command.extend(["-H", "X-GitHub-Api-Version: 2022-11-28"])
    command.append(f"/repos/{owner}/{repo}/tags")
    stdout = subprocess.check_output(command)

    tags = {}
    for tag_info in json.loads(stdout.decode("utf-8")):
        try:
            version = packaging.version.Version(tag_info["name"])
        except packaging.version.InvalidVersion:
            continue
        if version.is_prerelease or version.is_devrelease:
            continue
        sha = tag_info["commit"]["sha"]
        tags[version] = {
            "name": tag_info["name"],
            "sha": sha,
        }

    return tags
