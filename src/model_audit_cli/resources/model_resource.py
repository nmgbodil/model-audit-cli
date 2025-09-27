from typing import Any

from model_audit_cli.adapters.client import HFClient
from model_audit_cli.adapters.model_fetchers import HFModelFetcher
from model_audit_cli.errors import NOT_FOUND, AppError
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

    def fetch_metadata(self) -> Any:
        """Get model metadata from Huggingface API.

        Returns:
            Any: JSON object with models metadata.
        """
        if self.metadata is None:
            self.metadata = self._client.get_model_metadata(self._repo_id)

        return self.metadata

    def open_file(self, filename: str) -> str:
        """Opens and reads the content of a file from a specified repository.

        Args:
            filename (str): The name of the file to be opened and read.

        Returns:
            str: The content of the file as a string.

        Raises:
            AppError: If the file does not exist in the repository, an error is raised
                      with a NOT_FOUND status and additional context information.
        """
        text = None
        with HFModelFetcher(self._repo_id) as model:
            if model.exists(filename):
                text = model.read_text(filename)

        if text is not None:
            return text

        raise AppError(
            NOT_FOUND,
            f"{filename} does not exist in this repo.",
            context={"url": self.url},
        )

    def open_json_file(self, filename: str) -> Any:
        """Opens and reads a JSON file from a specified repository.

        Args:
            filename (str): The name of the JSON file to be opened.

        Returns:
            Any: The data read from the JSON file.

        Raises:
            AppError: If the specified file does not exist in the repository.
        """
        data = None
        with HFModelFetcher(self._repo_id) as model:
            if model.exists(filename):
                data = model.read_json(filename)

        if data is not None:
            return data

        raise AppError(
            NOT_FOUND,
            f"{filename} does not exist in this repo.",
            context={"url": self.url},
        )
