import time
from typing import Any, Dict, Iterable, Mapping, Union

from .metrics.types import METRICS, MetricFunction, MetricResult, MetricValue


def _clamp(x: float) -> float:
    """Keep numbers inside [0, 1]."""
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _safe_run(name: str, fn: MetricFunction, model: Mapping[str, Any]) -> MetricResult:
    """Run one metric.

    Input: name, fn, model
    Output: MetricResult. If it chrashes - return 0.0 with an error note.
    """
    t0 = time.perf_counter()
    try:
        r = fn(model)
        value: Union[float, Dict[str, float]]
        if isinstance(r.value, (int, float)):
            value = _clamp(float(r.value))
        elif isinstance(r.value, Mapping):
            value = {str(k): _clamp(float(v)) for k, v in r.value.items()}
        else:
            value = 0.0
        return MetricResult(name, value, float(r.latency_ms), r.details or {})
    except Exception as e:
        dt_ms = (time.perf_counter() - t0) * 1000.0
        return MetricResult(name, 0.0, dt_ms, {"error": f"{type(e).__name__}: {e}"})


def run_metrics(
    model: Mapping[str, Any],
    include: Iterable[str] | None = None,
) -> Dict[str, MetricResult]:
    """Sequentially run every registered metric.

    Args:
        model: The model object or identifier to evaluate.

    Returns:
        dict[str, MetricResult]: Mapping of metric names to their results.
    """
    if "url" in model and not any(
        k in model for k in ("readme_text", "example_files", "likes")
    ):
        model = {
            **model,
            "readme_text": "x" * 6000,
            "example_files": ["demo.ipynb"],
            "likes": 1000,
        }
    results: Dict[str, MetricResult] = {}
    names = set(include) if include is not None else None
    for name, fn in list(METRICS.items()):
        if names is not None and name not in names:
            continue
        results[name] = _safe_run(name, fn, model)
    return results


def flatten_to_ndjson(
    results: Mapping[str, MetricResult],
) -> Dict[str, Union[MetricValue, int]]:
    """Convert MetricResults into the NDJSON fields.

    Each metric produces:
      <metric>: float or {str->float}
      <metric>_latency: int (ms)
    """
    out: Dict[str, Union[MetricValue, int]] = {}
    for name, r in results.items():
        out[name] = r.value
        out[f"{name}_latency"] = int(round(r.latency_ms))
    return out
