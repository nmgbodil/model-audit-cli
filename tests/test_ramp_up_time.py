from pathlib import Path
from typing import Any, Iterator, Literal

import pytest

from model_audit_cli.metrics.ramp_up_time import RampUpTime


def make_fake_model(
    tmp_path: Path, with_readme: bool = True, num_model_files: int = 0
) -> Any:
    """Helper to create a fake Model-like object for testing."""

    repo_root = tmp_path
    if with_readme:
        (repo_root / "README.md").write_text("This is a test README file\n" * 100)

    # add model files
    (repo_root / "weights").mkdir(exist_ok=True)
    for i in range(num_model_files):
        (repo_root / "weights" / f"model_{i}.bin").write_text("fake-binary")

    class FakeModel:
        def __init__(self, root: Path) -> None:
            self.root = root

        def open_files(self) -> Any:
            root = self.root

            class Files:
                def __enter__(self) -> "Files":
                    return self

                def __exit__(
                    self,
                    exc_type: type[BaseException] | None,
                    exc: BaseException | None,
                    tb: Any,
                ) -> Literal[False]:
                    return False

                def file_exists(self, path: str) -> bool:
                    return (root / path).exists()

                def read_text(self, path: str, errors: str = "ignore") -> str:
                    return (root / path).read_text(errors=errors)

                def glob(self, pattern: str) -> list[Path]:
                    return list(root.glob(pattern))

            return Files()

    return FakeModel(repo_root)


def test_compute_with_readme_and_models(tmp_path: Path) -> None:
    fake_model = make_fake_model(tmp_path, with_readme=True, num_model_files=2)

    metric = RampUpTime()
    metric.compute(fake_model)

    assert isinstance(metric.value, float)
    assert 0 < metric.value <= 1
    assert metric.details["readme_length"] > 0
    assert metric.details["num_models"] == 2
    assert "readme_score" in metric.details
    assert "models_score" in metric.details


def test_compute_with_no_files(tmp_path: Path) -> None:
    fake_model = make_fake_model(tmp_path, with_readme=False, num_model_files=0)

    metric = RampUpTime()
    metric.compute(fake_model)

    assert metric.value == 0.0
    assert metric.details["readme_length"] == 0
    assert metric.details["num_models"] == 0
