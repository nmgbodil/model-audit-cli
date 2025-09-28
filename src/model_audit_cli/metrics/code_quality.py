from __future__ import annotations

import subprocess
import time
from typing import Any, Dict

from model_audit_cli.adapters.code_fetchers import open_codebase
from model_audit_cli.adapters.repo_view import RepoView
from model_audit_cli.resources.code_resource import CodeResource
from model_audit_cli.metrics.base_metric import Metric
from model_audit_cli.models import Model


class CodeQuality(Metric):
    """Metric for code quality: flake8 + mypy + stars/likes."""

    def __init__(self) -> None:
        super().__init__(name="code_quality")

    def _run_linter(self, repo: RepoView, cmd: list[str]) -> float:
        proc = subprocess.run(
            cmd,
            cwd=repo.root,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0:
            return 1.0
        errors = proc.stdout.count("\n") + proc.stderr.count("\n")

        if errors == 0:
            return 1.0
        if errors < 10:
            return 0.8
        if errors < 50:
            return 0.6
        return 0.4

    def _flake8_score(self, repo: RepoView) -> float:
        return self._run_linter(repo, ["flake8", "."])

    def _mypy_score(self, repo: RepoView) -> float:
        return self._run_linter(repo, ["mypy", "--strict", "."])

    def _stars_score(self, url: str) -> float:
        meta = CodeResource(url).fetch_metadata() or {}

        if "stargazers_count" in meta:      # GitHub
            raw = meta.get("stargazers_count", 0)
        elif "star_count" in meta:          # GitLab
            raw = meta.get("star_count", 0)
        elif "likes" in meta:               # Hugging Face
            raw = meta.get("likes", 0)
        else:
            raw = 0

        if raw <= 0:
            return 0.0
        if raw < 50:
            return 0.5
        return 1.0

    def compute(self, model: Model) -> CodeQuality:
        """Run code quality analysis on the model's code URL."""
        start = time.perf_counter()

        url = model.get("url")  # assumes model is dict-like
        if not url:
            self.value = 0.0
            self.latency_ms = int((time.perf_counter() - start) * 1000)
            self.details = {"error": "No code URL provided"}
            return self

        with open_codebase(url) as repo:
            flake8 = self._flake8_score(repo)
            mypy = self._mypy_score(repo)

        stars = self._stars_score(url)
        score = (flake8 + mypy + stars) / 3.0

        self.value = score
        self.latency_ms = int((time.perf_counter() - start) * 1000)
        self.details = {
            "flake8": flake8,
            "mypy": mypy,
            "stars": stars,
        }
        return self
