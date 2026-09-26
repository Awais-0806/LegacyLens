import httpx
from urllib.parse import urlparse
from app.services.url_validation import GitHubRepositoryURL


class FetchError(RuntimeError):
    pass


# GitHub always redirects archive URLs to a signed codeload URL.
# We follow redirects only to these hosts.
_ALLOWED_REDIRECT_HOSTS = {
    "github.com",
    "codeload.github.com",
    "objects.githubusercontent.com",
}


class GitHubFetcher:
    def __init__(self, timeout=30, max_bytes=100 * 1024 ** 2):
        self.timeout = timeout
        self.max_bytes = max_bytes

    def _resolve_default_branch(self, owner: str, repo: str) -> str:
        api = f"https://api.github.com/repos/{owner}/{repo}"
        try:
            r = httpx.get(
                api,
                timeout=min(self.timeout, 10),
                follow_redirects=True,
                headers={"Accept": "application/vnd.github+json"},
            )
            r.raise_for_status()
            return r.json().get("default_branch") or "main"
        except httpx.HTTPError:
            return "main"

    def _follow_redirects_to_zip(self, url: str) -> httpx.Response:
        with httpx.Client(timeout=self.timeout, follow_redirects=False) as c:
            for _ in range(5):
                r = c.get(url, headers={"Accept": "application/zip"})
                if r.status_code in (301, 302, 303, 307, 308):
                    loc = r.headers.get("location")
                    if not loc:
                        raise FetchError("Unsafe redirect rejected")
                    host = (urlparse(loc).hostname or "").lower()
                    if host not in _ALLOWED_REDIRECT_HOSTS:
                        raise FetchError("Unsafe redirect rejected")
                    url = loc
                    continue
                return r
            raise FetchError("Unsafe redirect rejected")

    def fetch(self, repo: GitHubRepositoryURL) -> tuple[bytes, str | None]:
        branch = self._resolve_default_branch(repo.owner, repo.repo)
        url = f"https://github.com/{repo.owner}/{repo.repo}/archive/refs/heads/{branch}.zip"
        try:
            r = self._follow_redirects_to_zip(url)
            r.raise_for_status()
            if len(r.content) > self.max_bytes:
                raise FetchError("Repository download limit exceeded")
            return r.content, None
        except httpx.HTTPError as e:
            raise FetchError("Repository could not be fetched") from e