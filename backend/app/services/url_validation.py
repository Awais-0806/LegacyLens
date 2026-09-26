from dataclasses import dataclass
from ipaddress import ip_address
from urllib.parse import urlparse
import re


_GITHUB_RE = re.compile(r"^/[A-Za-z0-9_.-]{1,100}/[A-Za-z0-9_.-]{1,100}/?$")
_BLOCKED_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "::1"}


@dataclass(frozen=True)
class GitHubRepositoryURL:
    owner: str
    repo: str
    canonical_url: str


def validate_public_github_url(raw_url: str) -> GitHubRepositoryURL:
    parsed = urlparse(raw_url)
    if parsed.scheme.lower() != "https":
        raise ValueError("Repository URL must use HTTPS")
    if parsed.username or parsed.password or parsed.port:
        raise ValueError("Repository URL must not contain credentials or a custom port")
    if parsed.query or parsed.fragment:
        raise ValueError("Repository URL must not contain query strings or fragments")
    host = (parsed.hostname or "").lower().rstrip(".")
    if host != "github.com":
        raise ValueError("Only github.com repositories are supported")
    if host in _BLOCKED_HOSTS:
        raise ValueError("Blocked host")
    try:
        parsed_ip = ip_address(host)
    except ValueError:
        parsed_ip = None
    if parsed_ip is not None and (parsed_ip.is_private or parsed_ip.is_loopback or parsed_ip.is_link_local):
        raise ValueError("Private or local hosts are not allowed")
    if not _GITHUB_RE.fullmatch(parsed.path):
        raise ValueError("Expected https://github.com/<owner>/<repo>")
    owner, repo = parsed.path.strip("/").split("/")
    if repo.endswith(".git"):
        repo = repo[:-4]
    if not repo:
        raise ValueError("Repository name is required")
    return GitHubRepositoryURL(owner=owner, repo=repo, canonical_url=f"https://github.com/{owner}/{repo}")
