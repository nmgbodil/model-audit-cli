# tests/test_size.py
from pathlib import Path
from typing import Any, Literal, cast

from model_audit_cli.metrics.size import DEVICE_BUDGETS, Size
from model_audit_cli.models import Model


class DummyRepo:
    """Fake repo that simulates files and sizes."""

    def __init__(self, files: dict[str, int]) -> None:
        """Initialize DummyRepo with a dict of files and their sizes in bytes."""
        self._files = files
        self.root = Path(".")

    def __enter__(self) -> "DummyRepo":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> Literal[False]:
        """Exit context manager (never suppress exceptions)."""
        return False

    def glob(self, pattern: str) -> list[Path]:
        """Return matching paths for the given glob pattern."""
        return [Path(fname) for fname in self._files if Path(fname).match(pattern)]

    def exists(self, filename: str) -> bool:
        """Return True if the filename exists in the repo."""
        return filename in self._files

    def read_text(self, filename: str) -> str:
        """Return dummy file text (not used in tests)."""
        return "dummy"

    def size_bytes(self, path: str) -> int:
        """Return the size in bytes for the given path."""
        return self._files.get(path, 0)


class DummyModel:
    """Fake Model that provides a dummy open_files context manager."""

    def __init__(
        self, files: dict[str, int] | None = None, raise_on_open: bool = False
    ) -> None:
        """Initialize DummyModel with files or simulate an error on open."""
        self._files = files or {}
        self._raise = raise_on_open

    def open_files(self) -> DummyRepo:
        """Return DummyRepo or raise if configured to simulate error."""
        if self._raise:
            raise RuntimeError("boom")
        return DummyRepo(self._files)


def test_size_computation_with_small_file() -> None:
    """Test Size metric with a repo containing one small file."""
    model = Model(model=DummyModel({"weights.bin": 1024}))  # type: ignore[arg-type]
    metric = Size()
    metric.compute(model)
    assert isinstance(metric.value, dict)
    for dev in DEVICE_BUDGETS:
        assert 0.0 <= metric.value[dev] <= 1.0
    assert metric.latency_ms >= 0


def test_size_computation_no_files() -> None:
    """Test Size metric when no model files are present."""
    model = Model(model=DummyModel({}))  # type: ignore[arg-type]
    metric = Size()
    metric.compute(model)
    value = cast(dict[str, float], metric.value)
    assert all(v == 1.0 for v in value.values())


def test_size_computation_error_path() -> None:
    """Test Size metric when open_files raises an exception."""
    model = Model(model=DummyModel(raise_on_open=True))  # type: ignore[arg-type]
    metric = Size()
    metric.compute(model)
    assert metric.value is None or isinstance(metric.value, dict)
