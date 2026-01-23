import typing as t

import requests


def get_tags_json(
    owner: str,
    repo: str,
) -> list[dict[str, t.Any]]:
    """Get recent tags for a repo."""

    endpoint = f"https://api.github.com/repos/{owner}/{repo}/tags/"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    response = requests.get(url=endpoint, headers=headers)

    return response.json()
