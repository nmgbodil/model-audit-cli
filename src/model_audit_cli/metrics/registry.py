from .base_metric import Metric

from .bus_factor import BusFactor
from .code_quality import CodeQuality
from .ramp_up_time import RampUpTime

ALL_METRICS: list[Metric] = [
    RampUpTime(),
    BusFactor(),
    CodeQuality(),
    # add more metrics here
]

METRICS_BY_NAME: dict[str, Metric] = {m.name: m for m in ALL_METRICS}
