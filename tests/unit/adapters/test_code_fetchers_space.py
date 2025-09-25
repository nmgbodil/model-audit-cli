from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from model_audit_cli.adapters.code_fetchers import open_codebase


@patch("model_audit_cli.adapters.model_fetchers.snapshot_download")
def test_hf_space_fetcher_uses_snapshot_download(
    snapshot_download_mock: MagicMock, tmp_path: Path
) -> None:
    """Test HF Space fetcher uses `snapshot_download` and reads files correctly."""
    fake_dir = tmp_path / "space_snapshot"
    fake_dir.mkdir()
    (fake_dir / "app.py").write_text("print('hi')\n", encoding="utf-8")
    (fake_dir / "README.md").write_text("# space\n", encoding="utf-8")

    snapshot_download_mock.return_value = str(fake_dir)

    url = "https://huggingface.co/spaces/acme/demo"
    with open_codebase(url) as view:
        assert view.read_text("app.py").startswith("print")
        assert view.read_text("README.md").startswith("# space")

    kwargs = snapshot_download_mock.call_args.kwargs
    assert kwargs["repo_type"] == "space"
    assert kwargs["repo_id"] == "acme/demo"
    assert kwargs["local_dir_use_symlinks"] is False
