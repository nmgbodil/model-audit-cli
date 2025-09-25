from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from utils import build_tgz, make_response

from model_audit_cli.adapters.code_fetchers import open_codebase


@patch("model_audit_cli.adapters.code_fetchers.requests.get")
def test_gitlab_api_archive_with_ref(mock_get: MagicMock) -> None:
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
def test_gitlab_http_error_maps_to_app_error(mock_get: MagicMock) -> None:
    """Test that HTTP errors from the GitLab API are correctly mapped to AppError."""
    from model_audit_cli.errors import HTTP_ERROR, AppError

    mock_get.return_value = make_response(status=403, text="Forbidden")

    with pytest.raises(AppError) as ei:
        with open_codebase("https://gitlab.com/org/proj", ref="main") as _:
            pass
    assert ei.value.code == HTTP_ERROR
