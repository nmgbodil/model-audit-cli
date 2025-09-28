from model_audit_cli.metrics.base_metric import Metric
from model_audit_cli.metrics.bus_factor import BusFactor
from model_audit_cli.metrics.code_quality import CodeQuality
from model_audit_cli.metrics.ramp_up_time import RampUpTime

ALL_METRICS: list[Metric] = [
    RampUpTime(),
    BusFactor(),
    CodeQuality(),
    # add more metrics here
]

METRICS_BY_NAME: dict[str, Metric] = {m.name: m for m in ALL_METRICS}
