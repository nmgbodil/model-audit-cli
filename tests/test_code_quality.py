from pathlib import Path
from typing import Any, Literal, Optional, Type
from unittest.mock import patch

import pytest

from model_audit_cli.metrics.code_quality import CodeQuality
from model_audit_cli.models import Model
from model_audit_cli.resources.model_resource import ModelResource


def test_code_quality_computes_scores(monkeypatch: Any, tmp_path: Path) -> None:
    # Arrange: create a dummy repo structure
    (tmp_path / "dummy.py").write_text("print('hello')")

    # DummyRepo that works as a context manager
    class DummyRepo:
        def __init__(self, root: Path) -> None:
            self.root = root

        def __enter__(self) -> "DummyRepo":
            return self

        def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc: Optional[BaseException],
            tb: Any,
        ) -> Literal[False]:
            return False  # don’t suppress exceptions

    def fake_open_codebase(url: str) -> DummyRepo:
        return DummyRepo(tmp_path)

    # Patch open_codebase to return DummyRepo
    monkeypatch.setattr(
        "model_audit_cli.metrics.code_quality.open_codebase", fake_open_codebase
    )

    # Patch linters to return fixed scores
    monkeypatch.setattr(CodeQuality, "_flake8_score", lambda self, repo: 0.8)
    monkeypatch.setattr(CodeQuality, "_mypy_score", lambda self, repo: 0.6)

    # Patch CodeResource metadata to simulate GitHub stars
    with patch(
        "model_audit_cli.metrics.code_quality.CodeResource.fetch_metadata",
        return_value={"stargazers_count": 24},
    ):
        metric = CodeQuality()

        fake_model = Model(model=ModelResource("https://huggingface.co/some/model"))

        # Act
        metric.compute(fake_model)

    # Assert
    assert isinstance(metric.value, float)
    assert 0 <= metric.value <= 1
    assert metric.details["flake8"] == 0.8
    assert metric.details["mypy"] == 0.6
    assert metric.details["stars"] == 0.5  # 24 stars → 0.5
