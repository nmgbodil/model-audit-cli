import pytest
from unittest.mock import patch

from model_audit_cli.metrics.code_quality import CodeQuality


def test_code_quality_computes_scores(monkeypatch, tmp_path):
    # Arrange: create a dummy repo structure
    (tmp_path / "dummy.py").write_text("print('hello')")

    # DummyRepo that works as a context manager
    class DummyRepo:
        def __init__(self, root):
            self.root = root
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc, tb):
            return False  # don’t suppress exceptions

    def fake_open_codebase(url: str):
        return DummyRepo(tmp_path)

    # Patch open_codebase to return DummyRepo
    monkeypatch.setattr("model_audit_cli.metrics.code_quality.open_codebase", fake_open_codebase)

    # Patch linters to return fixed scores
    monkeypatch.setattr(CodeQuality, "_flake8_score", lambda self, repo: 0.8)
    monkeypatch.setattr(CodeQuality, "_mypy_score", lambda self, repo: 0.6)

    # Patch CodeResource metadata to simulate GitHub stars
    with patch("model_audit_cli.metrics.code_quality.CodeResource.fetch_metadata", return_value={"stargazers_count": 24}):
        metric = CodeQuality()
        model = {"url": "https://github.com/some/repo"}

        # Act
        result = metric.compute(model)

    # Assert
    assert isinstance(result.value, float)
    assert 0 <= result.value <= 1
    assert result.details["flake8"] == 0.8
    assert result.details["mypy"] == 0.6
    assert result.details["stars"] == 0.5   # 24 stars → 0.5
