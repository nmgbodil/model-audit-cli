from typing import Any, Optional
from urllib.parse import urlparse

from pydantic import BaseModel


class _BaseResource(BaseModel):
    url: str
    metadata: Optional[dict[str, Any]] = None

    def _hf_id_from_url(self) -> str:
        path = urlparse(self.url)
        parts = [x for x in path.path.strip("/").split("/") if x]
        return f"{parts[1]}/{parts[2]}"

    def fetch_metadata(self) -> dict[str, Any]:
        raise NotImplementedError

    def open_file(self, filename: str) -> str:
        raise NotImplementedError
