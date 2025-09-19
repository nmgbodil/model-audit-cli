# src/model_audit_cli/metrics_engine.py

from __future__ import annotations

import logging
import time
from typing import Dict

from .types import METRICS, MetricResult

# Import metric modules for side effects (registration into METRICS).
# Add more imports here as new metric files are created.
from . import ramp_up_time as _metric_ramp_up_time  # noqa: F401


def _clamp(x: float) -> float:
    """Clamp numbers to [0, 1]."""
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _safe_run(name: str, fn, model: dict) -> MetricResult:
    """
    Run one metric with timing, clamping, and error capture.
    Returns a MetricResult even on failure (value=0.0 and details.error set).
    """
    log = logging.getLogger(__name__)
    t0 = time.perf_counter()
    log.debug("metric %s: start", name)

    try:
        # Call the metric function.
        r = fn(model)

        # Normalize/clamp value into the allowed shapes/range.
        value = r.value
        if isinstance(value, (int, float)):
            value = _clamp(float(value))
        elif isinstance(value, dict):
            value = {str(k): _clamp(float(v)) for k, v in value.items()}
        else:
            # Unknown type → neutralize to 0.0 but keep details.
            log.info("metric %s: unexpected value type %s; forcing to 0.0", name, type(value).__name__)
            value = 0.0

        dt_ms = (time.perf_counter() - t0) * 1000.0
        log.debug("metric %s: ok value=%r latency_ms=%.1f", name, value, dt_ms)

        # Preserve any details from the metric.
        details = getattr(r, "details", {}) or {}
        return MetricResult(name=name, value=value, latency_ms=dt_ms, details=details)

    except Exception as e:
        dt_ms = (time.perf_counter() - t0) * 1000.0
        log.info("metric %s: error %s (%.1f ms)", name, e, dt_ms)
        return MetricResult(
            name=name,
            value=0.0,
            latency_ms=dt_ms,
            details={"error": f"{type(e).__name__}: {e}"},
        )


def run_metrics(model: dict) -> Dict[str, MetricResult]:
    """
    Run all registered metrics (sequentially for now).
    Returns a dict: {metric_name: MetricResult}.
    """
    log = logging.getLogger(__name__)
    results: Dict[str, MetricResult] = {}

    metric_items = list(METRICS.items())
    log.debug("running %d metrics", len(metric_items))

    for name, fn in metric_items:
        results[name] = _safe_run(name, fn, model)

    log.debug("finished running metrics")
    return results


def flatten_to_ndjson(results: Dict[str, MetricResult]) -> dict:
    """
    Flatten MetricResults into the NDJSON fields:
      <metric>: float | {str->float}
      <metric>_latency: int (ms, rounded)
    """
    out: dict = {}
    for name, r in results.items():
        out[name] = r.value
        out[f"{name}_latency"] = int(round(r.latency_ms))
    return out
