from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from model_audit_cli.errors import NOT_FOUND, AppError
from model_audit_cli.resources.code_resource import CodeResource


class TestCodeResource:
    """Test cases for the CodeResource class."""

    @patch("model_audit_cli.resources.code_resource.HFClient.get_space_metadata")
    def test_fetch_metadata_hf_space(self, mock_space_meta: MagicMock) -> None:
        """Test successful retrieval of metadata for Hugging Face Spaces."""
        mock_space_meta.return_value = {"host": "hf_space", "name": "demo"}
        r = CodeResource("https://huggingface.co/spaces/acme/demo")

        meta = r.fetch_metadata()

        assert meta == {"host": "hf_space", "name": "demo"}
        # ensures _hf_id_from_url() was used (owner/name)
        mock_space_meta.assert_called_once_with("acme/demo")

    @patch("model_audit_cli.resources.code_resource.GitHubClient.get_metadata")
    def test_fetch_metadata_github(self, mock_meta: MagicMock) -> None:
        """Test successful retrieval of metadata for GitHub repositories."""
        mock_meta.return_value = {"host": "github", "default_branch": "main"}
        r = CodeResource("https://github.com/org/repo")

        meta = r.fetch_metadata()

        assert meta["host"] == "github"
        mock_meta.assert_called_once_with("https://github.com/org/repo")

    @patch("model_audit_cli.resources.code_resource.GitLabClient.get_metadata")
    def test_fetch_metadata_gitlab(self, mock_meta: MagicMock) -> None:
        """Test successful retrieval of metadata for GitLab repositories."""
        mock_meta.return_value = {"host": "gitlab", "default_branch": "main"}
        r = CodeResource("https://gitlab.com/group/sub/repo")

        meta = r.fetch_metadata()

        assert meta["host"] == "gitlab"
        mock_meta.assert_called_once_with("https://gitlab.com/group/sub/repo")

    @patch("model_audit_cli.resources.code_resource.GitHubClient.get_metadata")
    def test_fetch_metadata_cached_does_not_recall(self, mock_meta: MagicMock) -> None:
        """Test cached metadata is returned on subsequent calls without re-fetching."""
        mock_meta.return_value = {"host": "github"}
        r = CodeResource("https://github.com/org/repo")

        a = r.fetch_metadata()
        b = r.fetch_metadata()  # should use cached self.metadata

        assert a == b == {"host": "github"}
        mock_meta.assert_called_once_with("https://github.com/org/repo")

    @patch("model_audit_cli.resources.code_resource.open_codebase")
    def test_open_file_success(self, mock_open_codebase: MagicMock) -> None:
        """Test successful file opening and content retrieval."""
        # make the context manager yield a repo-like object
        cm = mock_open_codebase.return_value
        repo = MagicMock()
        repo.exists.return_value = True
        repo.read_text.return_value = "# code readme\n"
        cm.__enter__.return_value = repo

        r = CodeResource("https://github.com/org/repo")
        out = r.open_file("README.md")

        assert out == "# code readme\n"
        mock_open_codebase.assert_called_once_with("https://github.com/org/repo")
        repo.exists.assert_called_once_with("README.md")
        repo.read_text.assert_called_once_with("README.md")

    @patch("model_audit_cli.resources.code_resource.open_codebase")
    def test_open_file_not_found_raises(self, mock_open_codebase: MagicMock) -> None:
        """Test that AppError is raised when file is not found."""
        cm = mock_open_codebase.return_value
        repo = MagicMock()
        repo.exists.return_value = False
        cm.__enter__.return_value = repo

        r = CodeResource("https://gitlab.com/group/repo")
        with pytest.raises(AppError) as ei:
            _ = r.open_file("missing.txt")

        err = ei.value
        assert err.code == NOT_FOUND
        assert "missing.txt" in str(err)
        assert err.context is not None
        assert "url" in err.context
        assert err.context["url"].startswith("https://gitlab.com/")

    @patch("model_audit_cli.resources.code_resource.open_codebase")
    def test_open_json_success(self, mock_open_codebase: MagicMock) -> None:
        """Test successful JSON file opening and content retrieval."""
        cm = mock_open_codebase.return_value
        repo = MagicMock()
        repo.exists.return_value = True
        repo.read_json.return_value = {"tool": "gradio", "version": "4.x"}
        cm.__enter__.return_value = repo

        r = CodeResource("https://huggingface.co/spaces/acme/demo")
        obj = r.open_json("space_config.json")

        assert obj == {"tool": "gradio", "version": "4.x"}
        mock_open_codebase.assert_called_once_with(
            "https://huggingface.co/spaces/acme/demo"
        )
        repo.exists.assert_called_once_with("space_config.json")
        repo.read_json.assert_called_once_with("space_config.json")

    @patch("model_audit_cli.resources.code_resource.open_codebase")
    def test_open_json_not_found_raises(self, mock_open_codebase: MagicMock) -> None:
        """Test that AppError is raised when JSON file is not found."""
        cm = mock_open_codebase.return_value
        repo = MagicMock()
        repo.exists.return_value = False
        cm.__enter__.return_value = repo

        r = CodeResource("https://github.com/org/repo")
        with pytest.raises(AppError) as ei:
            _ = r.open_json("config.json")

        err = ei.value
        assert err.code == NOT_FOUND
        assert "config.json" in str(err)
        assert err.context is not None
        assert err.context["url"] == "https://github.com/org/repo"
