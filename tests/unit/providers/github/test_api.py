import responses

import upadup.providers.github.api


def test_gh_api_get_tags():
    responses.get("https://api.github.com/repos/a/b/tags/", json=[])
    assert isinstance(upadup.providers.github.api.get_tags_json("a", "b"), list)
