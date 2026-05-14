import pytest
import responses

import upadup.providers.github.api
import upadup.providers.github.errors


def test_gh_api_get_tags():
    responses.get("https://api.github.com/repos/a/b/tags", json=[])
    assert isinstance(upadup.providers.github.api.get_tags_json("a", "b"), list)


def test_gh_api_get_tags_404():
    """Verify that HTTP 404 raises GitHub404."""

    doc_url = "https://docs.github.com/rest/repos/repos#list-repository-tags"
    json = {"message": "Not Found", "documentation_url": doc_url, "status": "404"}
    responses.get("https://api.github.com/repos/a/b/tags", status=404, json=json)

    with pytest.raises(upadup.providers.github.errors.GitHub404):
        upadup.providers.github.api.get_tags_json("a", "b")
