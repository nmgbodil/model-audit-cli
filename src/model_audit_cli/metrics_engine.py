import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict    

from .metrics.base_metric import Metric
from .metrics.registry import ALL_METRICS



FORCE_SEQUENTIAL = os.environ.get("FORCE_SEQUENTIAL") == "1"


def _safe_run(metric: Metric, model: Dict[str, Any]) -> Metric:
    start = time.perf_counter()
    try:
        return metric.compute(model)
    except Exception as e:
        metric.value = 0.0
        metric.latency_ms = (time.perf_counter() - start) * 1000.0
        metric.details = {"error": str(e)}
        return metric


def compute_all_metrics(model: dict[str, Any], include: set[str] | None = None) -> dict[str, Metric]:
    results: dict[str, Metric] = {}
    metrics = [m for m in ALL_METRICS if include is None or m.name in include]

    if FORCE_SEQUENTIAL:
        for metric in metrics:
            results[metric.name] = _safe_run(metric, model)
    else:
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(_safe_run, metric, model): metric.name for metric in metrics}
        for future in as_completed(futures):
            metric = future.result()  # already Metric, no cast needed
            results[metric.name] = metric

    return results



def flatten_to_ndjson(results: Dict[str, Metric]) -> Dict[str, Any]:
    """Convert Metric objects into NDJSON-style flat dict."""
    out: Dict[str, Any] = {}
    for metric in results.values():
        out[metric.name] = metric.value
        out[f"{metric.name}_latency"] = int(round(metric.latency_ms))
        # optionally include details if you want:
        if metric.details:
            out[f"{metric.name}_details"] = metric.details
    return out
