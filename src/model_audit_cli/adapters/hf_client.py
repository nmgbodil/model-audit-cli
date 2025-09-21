import time
from typing import Any

import requests

from model_audit_cli.errors import SCHEMA_ERROR, AppError, http_error_from_hf_response


class HFClient:
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
        self.base_url = base_url.strip("/")

    def _get_json(self, path: str, retries: int, backoff: float = 2.0) -> Any:
        """Perform a GET request to the specified path and return the JSON response.

        Args:
            path (str): The API endpoint path.
            retries (Optional[int]): The number of retry attempts for failed requests.
                Defaults to 0.
            backoff (Optional[int]): The backoff multiplier for retry delays.
                Defaults to 2.

        Returns:
            Any: The JSON response from the API.

        Raises:
            AppError: If the response is not successful or the retries are exhausted.
        """
        url = self.base_url + path

        for attempt in range(retries + 1):
            try:
                response = requests.get(url)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as e:
                print(e)
                if response.status_code >= 500 and attempt < retries:
                    wait_time = backoff * 2**attempt
                    time.sleep(wait_time)
                    continue

                if response.status_code == 429 and attempt < retries:
                    wait_time = response.headers.get(
                        "Retry-After", backoff * 2**attempt
                    )
                    time.sleep(float(wait_time))
                    continue
                break
            except requests.exceptions.RequestException as e:
                print(e)
                if attempt < retries:
                    wait_time = backoff * 2**attempt
                    time.sleep(wait_time)
                else:
                    break

        raise http_error_from_hf_response(
            url=url, status=response.status_code, body=response.text
        )

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
                message="Unexpected shape for model metadata.",
                context={"url": f"{self.base_url}{path}", "type": type(data).__name__},
            )
        return data
