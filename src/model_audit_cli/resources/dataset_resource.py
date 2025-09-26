from typing import Any

from model_audit_cli.adapters.client import HFClient
from model_audit_cli.adapters.dataset_fetchers import HFDatasetFetcher
from model_audit_cli.errors import NOT_FOUND, AppError
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

    def fetch_metadata(self) -> Any:
        """Retrieve metadata associated with the dataset resource.

        Returns:
            Any: JSON object with models metadata.
        """
        if self.metadata is None:
            self.metadata = self._client.get_model_metadata(self._repo_id)

        return self.metadata

    def open_file(self, filename: str) -> str:
        """Opens and reads the content of a file from the dataset repository.

        Args:
            filename (str): The name of the file to be opened.

        Returns:
            str: The content of the file as a string.

        Raises:
            AppError: If the file does not exist in the dataset repository.
        """
        text = None
        with HFDatasetFetcher(self._repo_id) as dataset:
            if dataset.exists(filename):
                text = dataset.read_text(filename)

        if text is not None:
            return text

        raise AppError(
            NOT_FOUND,
            f"{filename} does not exist in this repo.",
            context={"url": self.url},
        )

    def open_json_file(self, filename: str) -> Any:
        """Opens and reads a JSON file from a specified dataset repository.

        Args:
            filename (str): The name of the JSON file to be opened.

        Returns:
            Any: The content of the JSON file.

        Raises:
            AppError: If the specified file does not exist in the dataset repository.
        """
        data = None
        with HFDatasetFetcher(self._repo_id) as dataset:
            if dataset.exists(filename):
                data = dataset.read_json(filename)

        if data is not None:
            return data

        raise AppError(
            NOT_FOUND,
            f"{filename} does not exist in this repo.",
            context={"url": self.url},
        )
