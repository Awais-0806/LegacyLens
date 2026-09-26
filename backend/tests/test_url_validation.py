import pytest

from app.services.url_validation import validate_public_github_url


def test_valid_github_url():
    result = validate_public_github_url("https://github.com/owner/repository")
    assert result.owner == "owner"
    assert result.repo == "repository"
    assert result.canonical_url == "https://github.com/owner/repository"


@pytest.mark.parametrize(
    "url",
    [
        "http://github.com/owner/repo",
        "https://evil.example/owner/repo",
        "file:///etc/passwd",
        "ftp://github.com/owner/repo",
        "https://github.com/owner/repo?redirect=http://127.0.0.1",
        "https://github.com:443/owner/repo",
        "https://github.com/owner",
    ],
)
def test_invalid_repository_urls(url):
    with pytest.raises(ValueError):
        validate_public_github_url(url)
