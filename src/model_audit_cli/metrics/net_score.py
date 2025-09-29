from __future__ import annotations

import statistics
import time
from typing import Dict, Optional

from model_audit_cli.metrics.base_metric import Metric

# Metric weights based on Sarah's priorities
METRIC_WEIGHTS: Dict[str, float] = {
    "license": 0.20,
    "ramp_up_time": 0.15,
    "bus_factor": 0.15,
    "dataset_and_code_score": 0.10,
    "dataset_quality": 0.10,
    "code_quality": 0.10,
    "performance_claims": 0.10,
    "size": 0.10,
}


class NetScore(Metric):
    """Aggregate metric runner for computing weighted net score."""

    def __init__(self) -> None:
        """Initialize available metrics."""
        """Initialize metric with name."""
        super().__init__(name="net_score")

    def evaluate(self, metrics: list[Metric]) -> None:
        """Run all metrics, aggregate results, and compute weighted net score.

        Args:
            urls: Dict with optional URLs for "model" and "code".

        Returns:
            Dict with individual metric values, latencies, and net_score fields.
        """
        start = time.perf_counter()
        self.value = 0

        for metric in metrics:
            if metric.name == "size" and isinstance(metric.value, dict):
                self.value += METRIC_WEIGHTS[metric.name] * statistics.mean(
                    metric.value.values()
                )
                continue
            if isinstance(metric.value, float):
                self.value += METRIC_WEIGHTS[metric.name] * metric.value
        self.latency_ms = int(round((time.perf_counter() - start) * 1000))


if __name__ == "__main__":
    scorer = NetScore()
    urls: Dict[str, Optional[str]] = {
        "model": "https://huggingface.co/google-bert/bert-base-uncased",
        "code": "https://huggingface.co/google-bert/bert-base-uncased",
    }
