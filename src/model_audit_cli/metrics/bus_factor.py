# src/model_audit_cli/metrics/bus_factor.py

import math
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from model_audit_cli.metrics.base_metric import Metric


class BusFactorScore(Metric):
    """Calculates the Bus Factor score."""

    def __init__(self) -> None:
        super().__init__("bus_factor")

    def compute(self, model: Dict[str, Any]) -> "BusFactorScore":
        """
        Compute the bus factor score based on:
          - contributors (int)
          - commits (int)
          - n_code (int, default 1)
          - lastModified (ISO8601 string, optional)
        """

        time_bf = time.time()

        #check if model, code, dataset are present 
        ...

        with model.model.fetch_metadata() as model_repo:
            last_modified_model: Optional[str] = model.get("lastModified")
        

        with model.code.fetch_metadata() as code_repo:
            last_modified_gh: Optional[str] = model.get("lastModified")

        with model.dataset.fetch_metadata() as dataset_repo:
            contributors: int = model.get("contributors", 1)
            commits: int = model.get("commits", 1)
            n_code: int = max(1, model.get("n_code", 1))
            last_modified: Optional[str] = model.get("lastModified")


        # normalize contributors (cap at 10)
        contributor_score = min(1.0, contributors / 10.0)

        # normalize commits (cap at 100)
        commit_score = min(1.0, commits / 100.0)

        # weighted average
        base_score = (0.5 * contributor_score + 0.5 * commit_score) / n_code

        # recency sub-score
        recency_score = 1.0
        if last_modified:
            try:
                dt = datetime.fromisoformat(last_modified.replace("Z", "+00:00"))
                days_since = (datetime.now(timezone.utc) - dt).days
                recency_score = math.exp(-math.log(2) * days_since / 365)
            except Exception:
                # fallback: ignore recency if parsing fails
                recency_score = 1.0

        final_score = max(0.0, min(1.0, base_score * recency_score))

        # set values
        self.value = final_score
        self.latency_ms = (time.time() - time_bf) * 1000
        self.details = {
            "contributors": contributors,
            "commits": commits,
            "n_code": n_code,
            "lastModified": last_modified,
            "base_score": base_score,
            "recency_score": recency_score,
        }

        return self
