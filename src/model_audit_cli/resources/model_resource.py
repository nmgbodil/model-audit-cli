from typing import Any

from model_audit_cli.adapters.hf_client import HFClient
from model_audit_cli.resources.base_resource import _BaseResource


class ModelResource(_BaseResource):
    """Represents a model resource for a machine learning model."""

    def __init__(self, url: str) -> None:
        """Initialize the model resource.

        Extracts the repository ID from the URL.
        """
        super().__init__(url=url)
        self._repo_id = self._hf_id_from_url()
        self._client = HFClient()

    def metadata(self) -> Any:
        """Get model metadata from Huggingface API.

        Returns:
            Any: JSON object with models metadata.
        """
        return self._client.get_model_metadata(self._repo_id)

    def open_file(self, filename: str) -> Any:
        """Open a file within the model resource.

        Args:
            filename (str): The name of the file to open.

        Returns:
            Any: The contents of the file.
        """
        pass
