import json
from typing import Any, Mapping, Optional

import requests


def make_hf_client_response(
    status: int,
    body: Any | None = None,
    text: str = "",
    url: str = "https://huggingface.co/api/models/test-repo",
    headers: Optional[Mapping[str, Any]] = None,
) -> requests.Response:
    """Create a mock HTTP response object with the given status, body, text, and URL.

    Args:
        status (int): The HTTP status code for the response.
        body (dict | None): The JSON body of the response. Defaults to None.
        text (str): The plain text content of the response. Defaults to an empty string.
        url (str): The URL associated with the response. Defaults to a test URL.

    Returns:
        requests.Response: A mock HTTP response object with the specified attributes.
    """
    response = requests.Response()
    response.status_code = status
    response.url = url
    if body is not None:
        response._content = json.dumps(body).encode()
        response.headers["Content-Type"] = "application/json"
    else:
        response._content = text.encode()

    if headers:
        response.headers.update(headers)
    return response
