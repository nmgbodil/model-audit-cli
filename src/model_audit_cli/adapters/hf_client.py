from typing import Any

from model_audit_cli.adapters.client import _Client
from model_audit_cli.errors import SCHEMA_ERROR, AppError


class HFClient(_Client):
    """A client for interacting with the Hugging Face API.

    Attributes:
        base_url (str): The base URL for the Hugging Face API.
    """

    def __init__(self, base_url: str = "https://huggingface.co"):
        """Initialize the HFClient with a base URL.

        Args:
            base_url (str): The base URL for the Hugging Face API.
                Defaults to "https://huggingface.co".
        """
        super().__init__(base_url=base_url)

    def get_model_metadata(self, repo_id: str, retries: int = 0) -> dict[str, Any]:
        """Retrieve metadata for a specific model from the Hugging Face API.

        Args:
            repo_id (str): The repository ID of the model.

        Returns:
            dict[str, Any]: The metadata of the model.

        Raises:
            AppError: If the response data is not a dictionary or if the request fails.
        """
        path = f"/api/models/{repo_id}"
        data = self._get_json(path, retries)
        if not isinstance(data, dict):
            raise AppError(
                code=SCHEMA_ERROR,
                message="Unexpected shape for model metadata.",
                context={"url": f"{self.base_url}{path}", "type": type(data).__name__},
            )
        return data

    def get_dataset_metadata(self, repo_id: str, retries: int = 0) -> dict[str, Any]:
        """Retrieve metadata for a specific dataset from the Hugging Face API.

        Args:
            repo_id (str): The repository ID of the dataset.

        Returns:
            dict[str, Any]: The metadata of the dataset.

        Raises:
            AppError: If the response data is not a dictionary or if the request fails.
        """
        path = f"/api/datasets/{repo_id}"
        data = self._get_json(path, retries)
        if not isinstance(data, dict):
            raise AppError(
                code=SCHEMA_ERROR,
                message="Unexpected shape for dataset metadata.",
                context={"url": f"{self.base_url}{path}", "type": type(data).__name__},
            )
        return data

    def get_space_metadata(self, repo_id: str, retries: int = 0) -> dict[str, Any]:
        """Retrieve metadata for a specific code space from the Hugging Face API.

        Args:
            repo_id (str): The repository ID of the code space.

        Returns:
            dict[str, Any]: The metadata of the code space.

        Raises:
            AppError: If the response data is not a dictionary or if the request fails.
        """
        path = f"/api/spaces/{repo_id}"
        data = self._get_json(path, retries)
        if not isinstance(data, dict):
            raise AppError(
                code=SCHEMA_ERROR,
                message="Unexpected shape for space metadata.",
                context={"url": f"{self.base_url}{path}", "type": type(data).__name__},
            )
        return data
