import json
import pathlib
import pytest
from src.model_audit_cli.models import Metrics

GOLDEN_FILE = pathlib.Path(__file__).parent / "golden" / "metrics.ndjson"


def test_golden_file_validates():
    with GOLDEN_FILE.open() as f:
        for i, line in enumerate(f, start=1):
            data = json.loads(line)
            try:
                Metrics(**data)  # validate with Pydantic
            except Exception as e:
                pytest.fail(f"Line {i} failed validation: {e}")
