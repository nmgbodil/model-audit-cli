from typing import Any

from model_audit_cli.adapters.client import GitHubClient, GitLabClient
from model_audit_cli.adapters.code_fetchers import open_codebase
from model_audit_cli.errors import NOT_FOUND, AppError
from model_audit_cli.resources.base_resource import _BaseResource


class CodeResource(_BaseResource):
    """Represents a code resource for a machine learning model."""

    def fetch_metadata(self) -> Any:
        """Retrieves metadata associated with the resource.

        Returns:
            Any: The metadata of the resource. The exact type and structure
            of the metadata depend on the specific implementation.
        """
        if self.metadata is None:
            if "github.com" in self.url:
                self.metadata = GitHubClient().get_metadata(self.url)
            elif "gitlab.com" in self.url:
                self.metadata = GitLabClient().get_metadata(self.url)

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
        with open_codebase(self.url) as code:
            if code.exists(filename):
                text = code.read_text(filename)

        if text is not None:
            return text

        raise AppError(
            NOT_FOUND,
            f"{filename} does not exist in this repo.",
            context={"url": self.url},
        )

    def open_json(self, filename: str) -> Any:
        """Opens and reads a JSON file from the codebase.

        Args:
            filename (str): The name of the JSON file to be opened.

        Returns:
            Any: The parsed JSON data from the file.

        Raises:
            AppError: If the specified file does not exist in the repository.
        """
        data = None
        with open_codebase(self.url) as code:
            if code.exists(filename):
                data = code.read_json(filename)

        if data is not None:
            return data

        raise AppError(
            NOT_FOUND,
            f"{filename} does not exist in this repo.",
            context={"url": self.url},
        )
