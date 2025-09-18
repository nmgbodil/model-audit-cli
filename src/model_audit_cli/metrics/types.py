# Keeps every metric consistent and type-annoted

from dataclasses import dataclass
from typing import Callable, Dict, Mapping, Union, Any

MetricValue = Union[float, Mapping[str, float]]

@dataclass
class MetricResult:
    """
    Metric result:
      - name: canonical metric key, e.g. "ramp_up_time"
      - value: float in [0,1] or a mapping[str,float]
      - latency_ms: wall time (ms)
      - details: optional debug info
    """
    name: str  
    value: MetricValue     
    latency_ms: float       
    details: dict[str, Any]    

MetricFunction = Callable[[dict], MetricResult]

METRICS: Dict[str, MetricFunction] = {}

def register(name: str):
    """Decorator to register a metric under its NDJSON key."""
    def deco(fn: MetricFunction):
        METRICS[name] = fn
        return fn
    return deco
