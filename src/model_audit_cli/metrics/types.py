from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Mapping, Union

MetricValue = Union[float, Mapping[str, float]]


@dataclass(slots=True)
class MetricResult:
    """Typed mapping for pre-metric scores and timings.

    Metric result:
      - name: canonical metric key, e.g. "ramp_up_time"
      - value: float in [0,1] or a mapping[str,float]
      - latency_ms: wall time (ms)
      - details: optional debug info
    """

    name: str
    value: MetricValue
    latency_ms: float
    details: Mapping[str, Any] = field(default_factory=dict)


MetricFunction = Callable[[Mapping[str, Any]], MetricResult]

METRICS: Dict[str, MetricFunction] = {}


def register(name: str) -> Callable[[MetricFunction], MetricFunction]:
    """Decorator to register a metric under its NDJSON key."""

    def deco(fn: MetricFunction) -> MetricFunction:
        METRICS[name] = fn
        return fn

    return deco
