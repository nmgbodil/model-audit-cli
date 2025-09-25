from typing import Any

from model_audit_cli.resources.base_resource import _BaseResource


class CodeResource(_BaseResource):
    """Represents a code resource for a machine learning model."""

    def metadata(self) -> Any:
        """Retrieves metadata associated with the resource.

        Returns:
            Any: The metadata of the resource. The exact type and structure
            of the metadata depend on the specific implementation.
        """
        pass

    def open_file(self, filename: str) -> Any:
        """Opens a file with the given filename.

        Args:
            filename (str): The name of the file to be opened.

        Returns:
            Any: The content of the file.
        """
        pass
