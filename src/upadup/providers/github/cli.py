import json
import shutil
import subprocess
import typing as t

HAS_CLI = None


def has_cli() -> bool:
    """Determine if the gh executable is available, and has a valid session active."""

    global HAS_CLI
    if HAS_CLI is not None:
        return HAS_CLI

    if shutil.which("gh") is None:
        HAS_CLI = False
    else:
        cmd = "gh auth status".split()
        completed_process = subprocess.run(cmd, capture_output=True)
        HAS_CLI = completed_process.returncode == 0

    return HAS_CLI


def get_tags_json(
    owner: str,
    repo: str,
) -> list[dict[str, t.Any]]:
    """Get recent tags for a repo."""

    command = ["gh", "api"]
    command.extend(["-H", "Accept: application/vnd.github+json"])
    command.extend(["-H", "X-GitHub-Api-Version: 2022-11-28"])
    command.append(f"/repos/{owner}/{repo}/tags")
    stdout = subprocess.check_output(command, encoding="utf-8")

    return json.loads(stdout)
