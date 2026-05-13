import typing as t

import requests

from .errors import GitHub404


def get_tags_json(
    owner: str,
    repo: str,
) -> list[dict[str, t.Any]]:
    """Get recent tags for a repo.

    :raises GitHub404: If the API call returns any status other than HTTP 200.
    """

    endpoint = f"https://api.github.com/repos/{owner}/{repo}/tags"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    response = requests.get(url=endpoint, headers=headers)
    if response.status_code == 200:
        return response.json()

    raise GitHub404()
