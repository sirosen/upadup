from . import api, gh


def get_latest_tag(string: str, *, freeze: bool = False) -> str:
    # Known formats:
    #
    #   github.com/{owner}/{repo}/{sub_path}@{tag}
    #
    uri, _, version = string.partition("@")
    host, owner, repo, *_ = uri.split("/")
    if host != "github.com":
        raise ValueError("Not a GitHub-based dependency")

    if gh.has_gh():
        tags = gh.get_tags(owner, repo)
    else:
        tags = api.get_tags(owner, repo)

    if not tags:
        return string

    max_version = max(tags)

    if freeze:
        sha = tags[max_version]["sha"]
        return f"{uri}@{sha}"

    name = tags[max_version]["name"]
    return f"{uri}@{name}"
