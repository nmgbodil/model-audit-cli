# Estimate how quick it is for an engineer to start using the model

import time
from .types import MetricResult, register


_LICENSE_SCORE = {
    "mit": 1.0, "apache-2.0": 0.95, "bsd-2-clause": 0.95, "bsd-3-clause": 0.95, "mpl-2.0": 0.9,
    "lgpl-2.1": 0.7, "lgpl-3.0": 0.7, "gpl-2.0": 0.35, "gpl-3.0": 0.3, "agpl-3.0": 0.25,
}

@register("ramp_up_time")
def ramp_up_time(model: dict) -> MetricResult:
    t0 = time.perf_counter()
    lic = (model.get("license") or "").lower()
    score = float(_LICENSE_SCORE.get(lic, 0.0))
    latency_ms = (time.perf_counter() - t0) * 1000.0
    return MetricResult("ramp_up_time", score, latency_ms, {"license": lic})
