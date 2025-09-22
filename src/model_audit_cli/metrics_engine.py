import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, Mapping, Union

from model_audit_cli.metrics.ramp_up_time import ramp_up_time

from .metrics.types import METRICS, MetricFunction, MetricResult, MetricValue

FORCE_SEQUENTIAL = os.environ.get("FORCE_SEQUENTIAL") == "1"

METRIC_FUNCS = {
    "ramp_up_time": ramp_up_time,
}


def _clamp(x: float) -> float:
    """Clamp a number to [0, 1]."""
    return max(0.0, min(1.0, x))


def _safe_run(
    metric: str, func: MetricFunction, model: Mapping[str, Any]
) -> MetricResult:
    """Run one metric safely and return a MetricResult."""
    start = time.perf_counter()
    try:
        r = func(model)

        if isinstance(r.value, (int, float)):
            value: Union[float, Dict[str, float]] = _clamp(float(r.value))
        elif isinstance(r.value, Mapping):
            value = {str(k): _clamp(float(v)) for k, v in r.value.items()}
        else:
            value = 0.0

        return MetricResult(metric, value, float(r.latency_ms), r.details or {})

    except Exception as e:
        latency = (time.perf_counter() - start) * 1000.0
        return MetricResult(metric, 0.0, latency, {"error": f"{type(e).__name__}: {e}"})


def run_metrics(
    model: Mapping[str, Any], include: set[str] | None = None
) -> Dict[str, MetricResult]:
    """Run metrics on a url.

    Uses parallel execution unless FORCE_SEQUENTIAL=1.
    """
    results: Dict[str, MetricResult] = {}
    metric_names = include if include else set(METRICS.keys())

    if FORCE_SEQUENTIAL:
        for metric, func in METRICS.items():
            if metric in metric_names:
                results[metric] = _safe_run(metric, func, model)

    else:
        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(_safe_run, metric, func, model): metric
                for metric, func in METRIC_FUNCS.items()
                if metric in metric_names
            }
            for future in as_completed(futures):
                metric = futures[future]
                try:
                    results[metric] = future.result()
                except Exception as e:
                    results[metric] = MetricResult(metric, 0.0, 0.0, {"error": str(e)})

    return results


def flatten_to_ndjson(
    results: Mapping[str, MetricResult],
) -> Dict[str, Union[MetricValue, int]]:
    """Convert MetricResults into NDJSON fields (<metric>, <metric>_latency)."""
    out: Dict[str, Union[MetricValue, int]] = {}
    for metric, r in results.items():
        out[metric] = r.value
        out[f"{metric}_latency"] = int(round(r.latency_ms))
    return out
