import packaging.version

from . import api, cli


def get_latest_tag(string: str, *, freeze: bool = False) -> str:
    # Known formats:
    #
    #   github.com/{owner}/{repo}/{sub_path}@{tag}
    #
    uri, _, _ = string.partition("@")
    host, owner, repo, *_ = uri.split("/")
    if host != "github.com":
        raise ValueError("Not a GitHub-based dependency")

    if cli.has_cli():
        response = cli.get_tags_json(owner, repo)
    else:
        response = api.get_tags_json(owner, repo)

    tags = {}
    for tag_info in response:
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

    if not tags:
        return string

    max_version = max(tags)

    if freeze:
        sha = tags[max_version]["sha"]
        return f"{uri}@{sha}"

    name = tags[max_version]["name"]
    return f"{uri}@{name}"
