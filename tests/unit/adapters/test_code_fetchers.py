from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from utils import build_tgz, make_response

from model_audit_cli.adapters.code_fetchers import open_codebase
from model_audit_cli.errors import UNSUPPORTED_URL, AppError


def test_open_codebase_unsupported_host() -> None:
    """Test that an unsupported host raises an AppError with the correct error code."""
    url = "https://bitbucket.org/team/repo"
    with pytest.raises(AppError) as ei:
        with open_codebase(url) as _:
            pass
    assert ei.value.code == UNSUPPORTED_URL


class TestHFSpaceFetcher:
    """Test cases for the HFSpaceFetcher."""

    @patch("model_audit_cli.adapters.model_fetchers.snapshot_download")
    def test_hf_space_fetcher_uses_snapshot_download(
        self, snapshot_download_mock: MagicMock, tmp_path: Path
    ) -> None:
        """Test HF Space fetcher uses `snapshot_download` and reads files correctly."""
        fake_dir = tmp_path / "space_snapshot"
        fake_dir.mkdir()
        (fake_dir / "app.py").write_text("print('hi')\n", encoding="utf-8")
        (fake_dir / "README.md").write_text("# space\n", encoding="utf-8")

        snapshot_download_mock.return_value = str(fake_dir)

        url = "https://huggingface.co/spaces/acme/demo"
        with open_codebase(url) as view:
            assert view.read_text("app.py").startswith("print")
            assert view.read_text("README.md").startswith("# space")

        kwargs = snapshot_download_mock.call_args.kwargs
        assert kwargs["repo_type"] == "space"
        assert kwargs["repo_id"] == "acme/demo"
        assert kwargs["local_dir_use_symlinks"] is False


class TestGitHubCodeFetcher:
    """Test cases for the GitHubCodeFetcher."""

    @patch("model_audit_cli.adapters.code_fetchers.requests.get")
    def test_github_tarball_happy_path(self, mock_get: MagicMock) -> None:
        """Test fetcher correctly fetches a tarball and reads its contents."""
        tgz = build_tgz({"README.md": b"# hello from GH\n"})
        mock = make_response(status=200, text="")
        mock._content = tgz
        mock_get.return_value = mock

        url = "https://github.com/someorg/somerepo"
        with open_codebase(url, ref="main") as view:
            assert view.read_text("README.md").startswith("# hello")

        called_url = mock_get.call_args[0][0]
        # Your code uses the GitHub API tarball URL
        assert "/repos/someorg/somerepo/tarball/main" in called_url

    @patch("model_audit_cli.adapters.code_fetchers.requests.get")
    def test_github_tree_revision_is_used(self, mock_get: MagicMock) -> None:
        """Test fetcher uses the correct revision when specified in the URL."""
        tgz = build_tgz({"README.md": b"# on CSP-3 branch\n"})
        mock = make_response(status=200, text="")
        mock._content = tgz
        mock_get.return_value = mock

        url = "https://github.com/acme/repo/tree/CSP-3-Email-verification"
        with open_codebase(url) as view:
            assert "CSP-3" in view.read_text("README.md")

        called_url = mock_get.call_args[0][0]
        assert "CSP-3-Email-verification" in called_url

    @patch("model_audit_cli.adapters.code_fetchers.requests.get")
    def test_github_http_error_maps_to_app_error(self, mock_get: MagicMock) -> None:
        """Test HTTP errors from the GitHub API are correctly mapped to AppError."""
        from model_audit_cli.errors import HTTP_ERROR, AppError

        mock_get.return_value = make_response(status=404, text="Not Found")

        with pytest.raises(AppError) as ei:
            with open_codebase("https://github.com/org/repo", ref="main") as _:
                pass
        assert ei.value.code == HTTP_ERROR


class TestGitLabCodeFetcher:
    """Test cases for the GitLabCodeFetcher."""

    @patch("model_audit_cli.adapters.code_fetchers.requests.get")
    def test_gitlab_api_archive_with_ref(self, mock_get: MagicMock) -> None:
        """Test GitLab code fetcher correctly fetches an archive with a specific ref."""
        tgz = build_tgz({"README.md": b"# GL readme\n"})
        mock = make_response(status=200, text="")
        mock._content = tgz
        mock_get.return_value = mock

        url = "https://gitlab.com/group/subgroup/proj"
        with open_codebase(url, ref="main") as view:
            assert view.read_text("README.md").startswith("# GL readme")

        called_url = mock_get.call_args[0][0]
        # Your implementation uses the GitLab API with ?sha=<ref>
        assert "/api/v4/projects/" in called_url
        assert "repository/archive.tar.gz" in called_url
        assert "sha=main" in called_url

    @patch("model_audit_cli.adapters.code_fetchers.requests.get")
    def test_gitlab_http_error_maps_to_app_error(self, mock_get: MagicMock) -> None:
        """Test HTTP errors from the GitLab API are correctly mapped to AppError."""
        from model_audit_cli.errors import HTTP_ERROR, AppError

        mock_get.return_value = make_response(status=403, text="Forbidden")

        with pytest.raises(AppError) as ei:
            with open_codebase("https://gitlab.com/org/proj", ref="main") as _:
                pass
        assert ei.value.code == HTTP_ERROR
