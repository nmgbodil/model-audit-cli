from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from model_audit_cli.adapters.model_fetchers import HFModelFetcher


@patch("model_audit_cli.adapters.model_fetchers.snapshot_download")
def test_model_fetcher_minimal(
    snapshot_download_mock: MagicMock, tmp_path: Path
) -> None:
    """Test that the model fetcher correctly fetches and reads model files."""
    root = tmp_path / "model"
    root.mkdir()
    (root / "README.md").write_text("# model\n", encoding="utf-8")
    (root / "config.json").write_text('{"a": 1}', encoding="utf-8")
    snapshot_download_mock.return_value = str(root)

    with HFModelFetcher("org/name") as view:
        assert view.read_text("README.md").startswith("# model")
        assert view.read_json("config.json")["a"] == 1

    kwargs = snapshot_download_mock.call_args.kwargs
    assert kwargs["repo_type"] == "model"
    assert kwargs["repo_id"] == "org/name"
    assert kwargs["local_dir_use_symlinks"] is False
    assert "allow_patterns" in kwargs
