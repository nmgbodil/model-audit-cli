from typing import Any

from model_audit_cli.adapters.client import HFClient
from model_audit_cli.resources.base_resource import _BaseResource


class CodeResource(_BaseResource):
    """Represents a code resource for a machine learning model."""

    def __init__(self, url: str):
        super().__init__(url=url)
        if self._is_hf_space_url():
            self._repo_id = self._hf_id_from_url()
            self._client = HFClient()

    def _is_hf_space_url(self) -> bool:
        """Check if the URL corresponds to a Hugging Face dataset.

        Returns:
            bool: True if the URL is a Hugging Face dataset URL, False otherwise.
        """
        return "huggingface.co/spaces/" in self.url

    def fetch_metadata(self) -> Any:
        """Retrieves metadata associated with the resource.

        Returns:
            Any: The metadata of the resource. The exact type and structure
            of the metadata depend on the specific implementation.
        """
        if self.metadata is None:
            if self._is_hf_space_url():
                self.metadata = self._client.get_space_metadata(self._repo_id)
            # NOTE: Add Image.NET and handle errors gracefully

        return self.metadata

    def open_file(self, filename: str) -> Any:
        """Opens a file with the given filename.

        Args:
            filename (str): The name of the file to be opened.

        Returns:
            Any: The content of the file.
        """
        pass
