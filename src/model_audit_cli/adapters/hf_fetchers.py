from __future__ import annotations

import tempfile
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Iterable, Optional

from huggingface_hub import snapshot_download

from model_audit_cli.adapters.repo_view import RepoView

MODEL_ALLOW = ["README.md", "README.*", "config.json", "model_index.json"]

DATASET_ALLOW = [
    "README.md",
    "README.*",
    "dataset_info.json",  # primary structured metadata
    "data/*",  # optional: small samples/processed shards if needed
]

MAX_FILE_BYTES = 256 * 1024


class _BaseSnapshotFetcher(AbstractContextManager[RepoView]):
    """Base class for fetching snapshots of Hugging Face repositories."""

    def __init__(
        self,
        repo_id: str,
        repo_type: str,
        revision: Optional[str],
        allow_patterns: Iterable[str],
        use_shared_cache: bool = True,
    ) -> None:
        """Initialize the snapshot fetcher with repository details and constraints.

        Args:
            repo_id (str): The ID of the repository to fetch.
            repo_type (str): The type of the repository (e.g., "model" or "dataset").
            revision (Optional[str]): The specific revision of the repository to fetch.
            allow_patterns (Iterable[str]): Patterns of files to allow in the snapshot.
            use_shared_cache (bool): Whether to use a shared cache for the snapshot.
                Defaults to True.
        """
        self.repo_id = repo_id
        self.repo_type = repo_type
        self.revision = revision
        self.allow_patterns = list(allow_patterns)
        self.use_shared_cache = use_shared_cache

        self._tmp_dir: Optional[tempfile.TemporaryDirectory[str]] = None
        self._local_path: Optional[Path] = None

    def __enter__(self) -> RepoView:
        """Enter the context manager and fetch the repository snapshot.

        Returns:
            RepoView: A view of the fetched repository.
        """
        self._tmp_dir = tempfile.TemporaryDirectory(prefix="mac_")
        target = Path(self._tmp_dir.name)

        local_path = Path(
            snapshot_download(
                repo_id=self.repo_id,
                repo_type=self.repo_type,
                revision=self.revision,
                allow_patterns=self.allow_patterns,
                local_dir=str(target),
                local_dir_use_symlinks=False,
            )
        )
        self._local_path = local_path

        # Remove any files that exceed the maximum file size
        for p in local_path.rglob("*"):
            if p.is_file() and p.stat().st_size > MAX_FILE_BYTES:
                p.unlink(missing_ok=True)

        return RepoView(local_path)

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
            self._local_path = None


class HFModelFetcher(_BaseSnapshotFetcher):
    """Fetcher for Hugging Face model repositories."""

    def __init__(
        self, repo_id: str, revision: Optional[str], use_shared_cache: bool = True
    ) -> None:
        """Initialize the model fetcher with repository details.

        Args:
            repo_id (str): The ID of the model repository to fetch.
            revision (Optional[str]):
                The specific revision of the model repository to fetch.
            use_shared_cache (bool): Whether to use a shared cache for the snapshot.
                Defaults to True.
        """
        super().__init__(repo_id, "model", revision, MODEL_ALLOW, use_shared_cache)


class HFDatasetFetcher(_BaseSnapshotFetcher):
    """Fetcher for Hugging Face dataset repositories."""

    def __init__(
        self, repo_id: str, revision: Optional[str], use_shared_cache: bool = True
    ) -> None:
        """Initialize the dataset fetcher with repository details.

        Args:
            repo_id (str): The ID of the dataset repository to fetch.
            revision (Optional[str]):
                The specific revision of the dataset repository to fetch.
            use_shared_cache (bool): Whether to use a shared cache for the snapshot.
                Defaults to True.
        """
        super().__init__(repo_id, "model", revision, DATASET_ALLOW, use_shared_cache)
