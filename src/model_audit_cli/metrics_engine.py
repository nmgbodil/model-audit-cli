import time
from .metrics.types import METRICS, MetricResult
from . import metrics as _load_metrics 


def _clamp(x: float) -> float:
    """
    Keep numbers inside [0, 1]
    """
    if x < 0.0: return 0.0
    if x > 1.0: return 1.0
    return x


def _safe_run(name, fn, model) -> MetricResult:
    """
    Run one metric. 
    Input: name, fn, model
    Output: MetricResult. If it chrashes - return 0.0 with an error note.
    """
    t0 = time.perf_counter()
    try:
        r = fn(model)  
        value = r.value

        if isinstance(value, (int, float)):
            value = _clamp(float(value))
        elif isinstance(value, dict):
            value = {str(k): _clamp(float(v)) for k, v in value.items()}
        else:
            value = 0.0 
        return MetricResult(name, value, float(r.latency_ms), r.details or {})
    except Exception as e:
        dt_ms = (time.perf_counter() - t0) * 1000.0
        return MetricResult(name, 0.0, dt_ms, {"error": f"{type(e).__name__}: {e}"})


def run_metrics(model: dict) -> dict:
    """
    Sequentially run every registered metric 
    Input: model
    Output: {name: MetricResult}
    """
    results = {}
    for name, fn in list(METRICS.items()):
        results[name] = _safe_run(name, fn, model)
    return results


def flatten_to_ndjson(results: dict) -> dict:
    """
    Turn MetricResults into the NDJSON fields:
      <metric>: float or {str->float}
      <metric>_latency: int (ms)
    """
    out = {}
    for name, r in results.items():
        out[name] = r.value
        out[f"{name}_latency"] = int(round(r.latency_ms))
    return out
