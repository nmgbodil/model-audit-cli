from typing import Any

from model_audit_cli.adapters.hf_client import HFClient
from model_audit_cli.resources.base_resource import _BaseResource


class DataResource(_BaseResource):
    """Represents a dataset resource for a machine learning model."""

    def __init__(self, url: str) -> None:
        """Initialize the dataset resource.

        If the URL is a Hugging Face dataset, the repository ID is extracted.
        """
        super().__init__(url=url)
        if self._is_hf_dataset_url():
            self._repo_id = self._hf_id_from_url()
            self._client = HFClient()

    def _is_hf_dataset_url(self) -> bool:
        """Check if the URL corresponds to a Hugging Face dataset.

        Returns:
            bool: True if the URL is a Hugging Face dataset URL, False otherwise.
        """
        return "huggingface.co/datasets/" in self.url

    def metadata(self) -> Any:
        """Get dataset metadata from Huggingface API.

        Returns:
            Any: JSON object with models metadata.
        """
        return self._client.get_model_metadata(self._repo_id)

    def open_file(self, filename: str) -> Any:
        """Open a file within the dataset resource.

        Args:
            filename (str): The name of the file to open.

        Returns:
            Any: The contents of the file.
        """
        pass
