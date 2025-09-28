from .base_metric import Metric
from .ramp_up_time import RampUpTime

ALL_METRICS: list[Metric] = [
    RampUpTime(),
    # add more metrics here
]

METRICS_BY_NAME: dict[str, Metric] = {m.name: m for m in ALL_METRICS}
