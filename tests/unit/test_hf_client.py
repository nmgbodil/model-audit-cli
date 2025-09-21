from unittest.mock import MagicMock, patch

import pytest
from utils import make_response

from model_audit_cli.adapters.hf_client import HFClient
from model_audit_cli.errors import SCHEMA_ERROR, AppError


@pytest.fixture
def hf_client() -> HFClient:
    """Fixture to create an instance of HFClient."""
    return HFClient()


class TestGetModelMetadata:
    """Test cases for the get_model_metadata method."""

    @patch("model_audit_cli.adapters.hf_client.requests.get")
    def test_success(self, mock_get: MagicMock, hf_client: HFClient) -> None:
        """Test successful retrieval of model metadata."""
        # Mock response
        mock_get.return_value = make_response(status=200, body={"name": "test-model"})

        # Call the method
        result = hf_client.get_model_metadata("test-repo")

        # Assertions
        assert result == {"name": "test-model"}
        mock_get.assert_called_once_with("https://huggingface.co/api/models/test-repo")

    @patch("model_audit_cli.adapters.hf_client.requests.get")
    def test_schema_error(self, mock_get: MagicMock, hf_client: HFClient) -> None:
        """Test schema error when retrieving model metadata."""
        # Mock response
        mock_get.return_value = make_response(status=200, body=["unexpected", "list"])

        # Call the method and assert exception
        with pytest.raises(AppError) as exc_info:
            hf_client.get_model_metadata("test-repo")

        assert exc_info.value.code == SCHEMA_ERROR
        mock_get.assert_called_once_with("https://huggingface.co/api/models/test-repo")

    @patch("model_audit_cli.adapters.hf_client.requests.get")
    def test_http_error(self, mock_get: MagicMock, hf_client: HFClient) -> None:
        """Test HTTP error when retrieving model metadata."""
        mock_get.return_value = make_response(404, text="Not Found")

        # Call the method and assert exception
        with pytest.raises(AppError):
            print(hf_client.get_model_metadata("test-repo"))

        mock_get.assert_called_once_with("https://huggingface.co/api/models/test-repo")


class TestGetDatasetMetadata:
    """Test cases for the get_dataset_metadata method."""

    @patch("model_audit_cli.adapters.hf_client.requests.get")
    def test_success(self, mock_get: MagicMock, hf_client: HFClient) -> None:
        """Test successful retrieval of dataset metadata."""
        # Mock response
        mock_get.return_value = make_response(status=200, body={"name": "test-dataset"})

        # Call the method
        result = hf_client.get_dataset_metadata("test-repo")

        # Assertions
        assert result == {"name": "test-dataset"}
        mock_get.assert_called_once_with(
            "https://huggingface.co/api/datasets/test-repo"
        )

    @patch("model_audit_cli.adapters.hf_client.requests.get")
    def test_schema_error(self, mock_get: MagicMock, hf_client: HFClient) -> None:
        """Test schema error when retrieving dataset metadata."""
        # Mock response
        mock_get.return_value = make_response(status=200, body=["unexpected", "list"])

        # Call the method and assert exception
        with pytest.raises(AppError) as exc_info:
            hf_client.get_dataset_metadata("test-repo")

        assert exc_info.value.code == SCHEMA_ERROR
        mock_get.assert_called_once_with(
            "https://huggingface.co/api/datasets/test-repo"
        )

    @patch("model_audit_cli.adapters.hf_client.requests.get")
    def test_http_error(self, mock_get: MagicMock, hf_client: HFClient) -> None:
        """Test HTTP error when retrieving dataset metadata."""
        # Mock response
        mock_get.return_value = make_response(status=500, text="Internal Server Error")

        # Call the method and assert exception
        with pytest.raises(AppError):
            hf_client.get_dataset_metadata("test-repo")

        mock_get.assert_called_once_with(
            "https://huggingface.co/api/datasets/test-repo"
        )
