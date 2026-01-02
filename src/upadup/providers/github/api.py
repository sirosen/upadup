import packaging.version
import requests


def get_tags(owner: str, repo: str) -> dict[packaging.version.Version, dict[str, str]]:
    """Get recent tags for a repo."""

    endpoint = f"https://api.github.com/repos/{owner}/{repo}/tags/"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    response = requests.get(url=endpoint, headers=headers)

    tags = {}
    for tag_info in response.json():
        try:
            version = packaging.version.Version(tag_info["name"])
        except packaging.version.InvalidVersion:
            continue
        sha = tag_info["commit"]["sha"]
        tags[version] = {
            "name": tag_info["name"],
            "sha": sha,
        }

    return tags
