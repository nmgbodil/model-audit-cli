from model_audit_cli.metrics_engine import flatten_to_ndjson, run_metrics


def test_engine_constant_output() -> None:
    """Dummy test engine."""
    ctx = {"url": "https://huggingface.co/google/gemma-3-270m/tree/main"}
    results = run_metrics(ctx, include=["ramp_up_time", "bus_factor"])
    out = flatten_to_ndjson(results)
    assert out["ramp_up_time"] == 1.0
    assert out["bus_factor"] == 1.0
