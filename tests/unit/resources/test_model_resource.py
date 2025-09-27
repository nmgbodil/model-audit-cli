from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from model_audit_cli.errors import NOT_FOUND, AppError
from model_audit_cli.resources.model_resource import ModelResource


class TestModelResource:
    """Test cases for the ModelResource class."""

    @patch("model_audit_cli.resources.model_resource.HFClient.get_model_metadata")
    def test_metadata_calls_hfclient(self, mock_get: MagicMock) -> None:
        """Test fetch_metadata calls HFClient.get_model_metadata with right params."""
        mock_get.return_value = {"name": "bert-base-uncased"}
        r = ModelResource("https://huggingface.co/google-bert/bert-base-uncased")

        meta = r.fetch_metadata()

        assert meta["name"] == "bert-base-uncased"
        mock_get.assert_called_once_with("google-bert/bert-base-uncased")

    @patch("model_audit_cli.resources.model_resource.HFModelFetcher")
    def test_open_file_returns_text(self, mock_fetcher: MagicMock) -> None:
        """Test that open_file returns text content from model files."""
        r = ModelResource("https://huggingface.co/google-bert/bert-base-uncased")

        # Make the context manager yield an object with read_text/read_json
        cm = mock_fetcher.return_value
        repo_like = MagicMock()
        repo_like.read_text.return_value = "# model readme\n"
        cm.__enter__.return_value = repo_like

        out = r.open_file("README.md")
        assert out == "# model readme\n"

        mock_fetcher.assert_called_once_with("google-bert/bert-base-uncased")
        repo_like.read_text.assert_called_once_with("README.md")

    @patch("model_audit_cli.resources.model_resource.HFModelFetcher")
    def test_open_json_file_returns_object(self, mock_fetcher: MagicMock) -> None:
        """Test that open_json_file returns parsed JSON object from model files."""
        r = ModelResource("https://huggingface.co/google-bert/bert-base-uncased")

        cm = mock_fetcher.return_value
        repo_like = MagicMock()
        repo_like.read_json.return_value = {"a": 1, "b": [2, 3]}
        cm.__enter__.return_value = repo_like

        obj = r.open_json_file("config.json")
        assert obj == {"a": 1, "b": [2, 3]}

        mock_fetcher.assert_called_once_with("google-bert/bert-base-uncased")
        repo_like.read_json.assert_called_once_with("config.json")

    @patch("model_audit_cli.resources.model_resource.HFClient.get_model_metadata")
    def test_fetch_metadata_cached(self, mock_get: MagicMock) -> None:
        """Test cached metadata is returned on subsequent calls without re-fetching."""
        mock_get.return_value = {"once": True}
        r = ModelResource("google-bert/bert-base-uncased")

        a = r.fetch_metadata()
        b = r.fetch_metadata()  # should not call client again

        assert a == b == {"once": True}
        mock_get.assert_called_once_with("google-bert/bert-base-uncased")

    @patch("model_audit_cli.resources.model_resource.HFModelFetcher")
    def test_open_file_success(self, mock_fetcher: MagicMock) -> None:
        """Test successful file opening and content retrieval from model."""
        cm = mock_fetcher.return_value
        repo = MagicMock()
        repo.exists.return_value = True
        repo.read_text.return_value = "# model readme\n"
        cm.__enter__.return_value = repo

        r = ModelResource("google-bert/bert-base-uncased")
        out = r.open_file("README.md")

        assert out == "# model readme\n"
        mock_fetcher.assert_called_once_with("google-bert/bert-base-uncased")
        repo.exists.assert_called_once_with("README.md")
        repo.read_text.assert_called_once_with("README.md")

    @patch("model_audit_cli.resources.model_resource.HFModelFetcher")
    def test_open_file_empty_string_is_valid(self, mock_fetcher: MagicMock) -> None:
        """Test that empty string content is valid and returned correctly."""
        cm = mock_fetcher.return_value
        repo = MagicMock()
        repo.exists.return_value = True
        repo.read_text.return_value = ""  # empty content should still return
        cm.__enter__.return_value = repo

        r = ModelResource("google-bert/bert-base-uncased")
        out = r.open_file("EMPTY.md")

        assert out == ""
        repo.exists.assert_called_once_with("EMPTY.md")
        repo.read_text.assert_called_once_with("EMPTY.md")

    @patch("model_audit_cli.resources.model_resource.HFModelFetcher")
    def test_open_file_not_found_raises(self, mock_fetcher: MagicMock) -> None:
        """Test that AppError is raised when file is not found in model."""
        cm = mock_fetcher.return_value
        repo = MagicMock()
        repo.exists.return_value = False
        cm.__enter__.return_value = repo

        r = ModelResource("google-bert/bert-base-uncased")
        with pytest.raises(AppError) as ei:
            _ = r.open_file("missing.txt")

        err = ei.value
        assert err.code == NOT_FOUND
        assert "missing.txt" in str(err)
        assert err.context is not None
        assert err.context["url"].endswith("google-bert/bert-base-uncased")

    @patch("model_audit_cli.resources.model_resource.HFModelFetcher")
    def test_open_json_file_success(self, mock_fetcher: MagicMock) -> None:
        """Test successful JSON file opening and content retrieval from model."""
        cm = mock_fetcher.return_value
        repo = MagicMock()
        repo.exists.return_value = True
        repo.read_json.return_value = {"a": 1, "b": [2, 3]}
        cm.__enter__.return_value = repo

        r = ModelResource("google-bert/bert-base-uncased")
        obj = r.open_json_file("config.json")

        assert obj == {"a": 1, "b": [2, 3]}
        mock_fetcher.assert_called_once_with("google-bert/bert-base-uncased")
        repo.exists.assert_called_once_with("config.json")
        repo.read_json.assert_called_once_with("config.json")

    @patch("model_audit_cli.resources.model_resource.HFModelFetcher")
    def test_open_json_file_empty_object_is_valid(
        self, mock_fetcher: MagicMock
    ) -> None:
        """Test that empty JSON object is valid and returned correctly."""
        cm = mock_fetcher.return_value
        repo = MagicMock()
        repo.exists.return_value = True
        repo.read_json.return_value = {}  # empty JSON should still return
        cm.__enter__.return_value = repo

        r = ModelResource("google-bert/bert-base-uncased")
        obj = r.open_json_file("empty.json")

        assert obj == {}
        repo.exists.assert_called_once_with("empty.json")
        repo.read_json.assert_called_once_with("empty.json")

    @patch("model_audit_cli.resources.model_resource.HFModelFetcher")
    def test_open_json_file_not_found_raises(self, mock_fetcher: MagicMock) -> None:
        """Test that AppError is raised when JSON file is not found in model."""
        cm = mock_fetcher.return_value
        repo = MagicMock()
        repo.exists.return_value = False
        cm.__enter__.return_value = repo

        r = ModelResource("google-bert/bert-base-uncased")
        with pytest.raises(AppError) as ei:
            _ = r.open_json_file("absent.json")

        err = ei.value
        assert err.code == NOT_FOUND
        assert "absent.json" in str(err)
        assert err.context is not None
        assert err.context["url"].endswith("google-bert/bert-base-uncased")
