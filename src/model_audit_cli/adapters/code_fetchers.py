from __future__ import annotations

import io
import tarfile
import tempfile
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Any, ContextManager, Mapping, Optional
from urllib.parse import urlparse

import requests
from dulwich import porcelain

from model_audit_cli.adapters.model_fetchers import _BaseSnapshotFetcher
from model_audit_cli.adapters.repo_view import RepoView
from model_audit_cli.errors import HTTP_ERROR, NETWORK_ERROR, UNSUPPORTED_URL, AppError

SPACE_ALLOW = ["app.*", "requirements*.txt", "runtime.txt", "*.py", "README.*"]


def open_codebase(
    url: str,
    *,
    need_history: bool = False,
    ref: Optional[str] = None,
    token: Optional[str] = None,
) -> ContextManager[RepoView]:
    """Open a codebase and return a context manager for interacting with it.

    This function determines the type of codebase (e.g., GitHub, GitLab, Hugging Face
    Space) based on the provided URL and returns an appropriate context manager for
    interacting with the codebase. The context manager provides access to the
    repository's files and metadata.

    Args:
        url (str): The URL of the codebase to open.
        need_history (bool): Whether to fetch the full commit history.
            Defaults to False.
        ref (Optional[str]): The branch, tag, or commit to fetch. Defaults to None.
        token (Optional[str]): An optional authentication token for private
            repositories.

    Returns:
        ContextManager[RepoView]: A context manager for interacting with the codebase.

    Raises:
        AppError: If the URL is unsupported or invalid.
    """
    host, parts = _parse(url)
    if _is_hf_space(host, parts):
        return _HFSpaceFetcher(f"{parts[1]}/{parts[2]}", _extract_rev(parts))
    if host.endswith("github.com"):
        owner, repo = parts[0], parts[1]
        revision = _extract_rev(parts) or ref
        return _GitHubCodeFetcher(owner, repo, revision, need_history, token)
    if host.endswith("gitlab.com"):
        ns_name = parts[0]
        revision = _extract_rev(parts) or ref
        return _GitLabCodeFetcher(ns_name, revision, need_history, token)

    raise AppError(UNSUPPORTED_URL, "Unsupported codebase url link")


def _parse(url: str) -> tuple[str, list[str]]:
    p = urlparse(url)
    return p.netloc.lower(), [x for x in p.path.strip("/").split("/") if x]


def _is_hf_space(host: str, parts: list[str]) -> bool:
    return host == "huggingface.co" and len(parts) >= 3 and parts[0] == "spaces"


def _extract_rev(parts: list[str]) -> Optional[str]:
    for i in range(len(parts) - 1):
        if parts[i] in {"tree", "blob", "resolve"}:
            return parts[i + 1]
    return None


class _HFSpaceFetcher(_BaseSnapshotFetcher):
    """Fetcher for Hugging Face Space repositories."""

    def __init__(
        self, repo_id: str, revision: Optional[str], use_shared_cache: bool = True
    ) -> None:
        """Initialize the space fetcher with repository details.

        Args:
            repo_id (str): The ID of the space repository to fetch.
            revision (Optional[str]):
                The specific revision of the space repository to fetch.
            use_shared_cache (bool): Whether to use a shared cache for the snapshot.
                Defaults to True.
        """
        super().__init__(repo_id, "space", revision, SPACE_ALLOW, use_shared_cache)


class _GitHubCodeFetcher(AbstractContextManager[RepoView]):
    """A context manager for fetching and extracting GitHub repositories as tarballs.

    This class supports two modes of operation:
    1. Full repository clone with commit history.
    2. Fast tarball download for file-only access.
    """

    def __init__(
        self,
        owner: str,
        repo: str,
        ref: Optional[str],
        need_history: bool,
        token: Optional[str] = None,
    ) -> None:
        """Initialize the GitHubCodeFetcher with repository details.

        Args:
            owner (str): The owner of the GitHub repository.
            repo (str): The name of the GitHub repository.
            ref (Optional[str]): The branch, tag, or commit to fetch.
                Defaults to "main".
            token (Optional[str]): A GitHub personal access token for authentication.
            need_history (bool): Whether to fetch the full commit history.
        """
        self.owner = owner
        self.repo = repo
        self.ref = ref or "main"
        self.token = token
        self.need_history = need_history
        self._tmp_dir: Optional[tempfile.TemporaryDirectory[str]] = None
        self._root: Optional[Path] = None

    def __enter__(self) -> RepoView:
        self._tmp_dir = tempfile.TemporaryDirectory(prefix="mac")
        root = Path(self._tmp_dir.name)

        # If we need commit history and actual repo
        if self.need_history:
            dest = root / "repo"
            porcelain.clone(
                f"https://github.com/{self.owner}/{self.repo}.git", target=str(dest)
            )
            if self.ref not in {"main", "master", "HEAD"}:
                porcelain.checkout(str(dest), self.ref)
            self._root = dest
            return RepoView(dest)

        # If we need files only: fast tarball download
        url = (
            f"https://api.github.com/repos/{self.owner}/{self.repo}/tarball/{self.ref}"
        )
        headers = {"Accept": "application/vnd.github+json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        _extract_tarball(url, headers, root)
        self._root = _top_dir(root)
        return RepoView(self._root)

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[object],
    ) -> None:
        try:
            if self._tmp_dir:
                self._tmp_dir.cleanup()
        finally:
            self._tmp_dir = None
            self._root = None


class _GitLabCodeFetcher(AbstractContextManager[RepoView]):
    """A context manager for fetching and extracting GitLab repositories as a tar.gz.

    This class supports two modes of operation:
    1. Full repository clone with commit history.
    2. Fast tarball download for file-only access.
    """

    def __init__(
        self,
        ns_name: str,
        ref: Optional[str],
        need_history: bool,
        token: Optional[str] = None,
    ) -> None:
        """Initialize the GitLabCodeFetcher with repository details.

        Args:
            ns_name (str): The namespace of the GitHub repository.
            ref (Optional[str]): The branch, tag, or commit to fetch.
                Defaults to "main".
            token (Optional[str]): A GitHub personal access token for authentication.
            need_history (bool): Whether to fetch the full commit history.
        """
        self.ns_name = ns_name
        self.ref = ref or "main"
        self.token = token
        self.need_history = need_history
        self._tmp_dir: Optional[tempfile.TemporaryDirectory[str]] = None
        self._root: Optional[Path] = None

    def __enter__(self) -> RepoView:
        self._tmp_dir = tempfile.TemporaryDirectory(prefix="mac_")
        root = Path(self._tmp_dir.name)

        # If we need commit history and actual repo
        if self.need_history:
            dest = root / "repo"
            porcelain.clone(f"https://gitlab.com/{self.ns_name}.git", target=str(dest))
            if self.ref not in {"main", "master", "HEAD"}:
                porcelain.checkout(str(dest), self.ref)
            self._root = dest
            return RepoView(dest)

        # If we need files only: fast tarball download
        url = (
            f"https://gitlab.com/{self.ns_name}/-/archive/{self.ref}"
            + f"/{self.ns_name.split('/')[-1]}-{self.ref}.tar.gz"
        )
        headers = {}
        if self.token:
            headers["PRIVATE-TOKEN"] = self.token

        _extract_tarball(url, headers, root)
        self._root = _top_dir(root)
        return RepoView(self._root)

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[object],
    ) -> None:
        try:
            if self._tmp_dir:
                self._tmp_dir.cleanup()
        finally:
            self._tmp_dir = None
            self._root = None


def _extract_tarball(url: str, headers: Mapping[str, Any], dest: Path) -> None:
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        raise AppError(
            HTTP_ERROR,
            f"GitHub returned HTTP {response.status_code} for tarball.",
            context={"url": url},
        )
    except requests.RequestException as e:
        raise AppError(
            NETWORK_ERROR,
            "Network error fetching GitHub tarball.",
            cause=e,
            context={"url": url},
        )

    with tarfile.open(fileobj=io.BytesIO(response.content), mode="r:gz") as tf:
        tf.extractall(dest)


def _top_dir(root: Path) -> Path:
    dirs = [p for p in root.iterdir() if p.is_dir()]
    return dirs[0] if dirs else root


if __name__ == "__main__":
    url = "https://github.com/nmgbodil/the-hub/tree/CSP-3-Email-verification"
    with open_codebase(url, need_history=True) as code:
        text = code.read_text("auth.py")

    print(text)
