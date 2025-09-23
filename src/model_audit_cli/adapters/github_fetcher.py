from __future__ import annotations

import io
import tarfile
import tempfile
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Optional

import requests

from model_audit_cli.adapters.repo_view import RepoView
from model_audit_cli.errors import HTTP_ERROR, NETWORK_ERROR, AppError

GITHUB_API = "https://api/github.com"


class GitHubCodeFetcher(AbstractContextManager[RepoView]):
    """A context manager for fetching and extracting GitHub repositories as tarballs."""

    def __init__(
        self, owner: str, repo: str, ref: Optional[str], token: Optional[str]
    ) -> None:
        """Initialize the GitHubCodeFetcher with repository details.

        Args:
            owner (str): The owner of the GitHub repository.
            repo (str): The name of the GitHub repository.
            ref (Optional[str]): The branch, tag, or commit to fetch.
                Defaults to "main".
            token (Optional[str]): A GitHub personal access token for authentication.
        """
        self.owner = owner
        self.repo = repo
        self.ref = ref or "main"
        self.token = token
        self._tmp_dir: Optional[tempfile.TemporaryDirectory[str]] = None
        self._root: Optional[Path] = None

    def __enter__(self) -> RepoView:
        """Enter the context manager and fetch the repository tarball.

        Returns:
            RepoView: A view of the extracted repository files.

        Raises:
            AppError: If there is an HTTP or network error while fetching the tarball.
        """
        self._tmp_dir = tempfile.TemporaryDirectory(prefix="mac_")
        root = Path(self._tmp_dir.name)

        url = f"{GITHUB_API}/repos/{self.owner}/{self.repo}/tarball/{self.ref}"
        headers = {"Accept": "application/vnd.github+json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

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
            tf.extractall(root)

        [top] = [p for p in root.iterdir() if p.is_dir()]
        self._root = top
        return RepoView(top)

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[object],
    ) -> None:
        """Exit the context manager and clean up temporary resources.

        Args:
            exc_type (Optional[type[BaseException]]):
                The exception type, if an exception occurred.
            exc_value (Optional[BaseException]):
                The exception instance, if an exception occurred.
            traceback (Optional[object]):
                The traceback object, if an exception occurred.

        Returns:
            None
        """
        if exc_value:
            raise exc_value

        try:
            if self._tmp_dir:
                self._tmp_dir.cleanup()
        finally:
            self._tmp_dir = None
            self._root = None
