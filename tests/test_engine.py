import model_audit_cli.metrics_engine as metrics_engine
from model_audit_cli.models import Model
from model_audit_cli.resources.model_resource import ModelResource
from model_audit_cli.log import logger

def test_engine_constant_output() -> None:
    """Dummy test engine."""
    fake_model = Model(
        model=ModelResource("https://huggingface.co/google/gemma-3-270m")
    )

    # include should be a set or None
    results = metrics_engine.compute_all_metrics(fake_model, include=None)

    out = metrics_engine.flatten_to_ndjson(results)
    assert out["ramp_up_time"] == 0.0
