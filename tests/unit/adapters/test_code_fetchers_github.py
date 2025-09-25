from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from utils import build_tgz, make_response

from model_audit_cli.adapters.code_fetchers import open_codebase


@patch("model_audit_cli.adapters.code_fetchers.requests.get")
def test_github_tarball_happy_path(mock_get: MagicMock) -> None:
    """Test GitHub code fetcher correctly fetches a tarball and reads its contents."""
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
def test_github_tree_revision_is_used(mock_get: MagicMock) -> None:
    """Test GitHub code fetcher uses the correct revision when specified in the URL."""
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
def test_github_http_error_maps_to_app_error(mock_get: MagicMock) -> None:
    """Test that HTTP errors from the GitHub API are correctly mapped to AppError."""
    from model_audit_cli.errors import HTTP_ERROR, AppError

    mock_get.return_value = make_response(status=404, text="Not Found")

    with pytest.raises(AppError) as ei:
        with open_codebase("https://github.com/org/repo", ref="main") as _:
            pass
    assert ei.value.code == HTTP_ERROR
