import pytest
from model_audit_cli.metrics_engine import run_metrics, flatten_to_ndjson
from model_audit_cli.metrics.ramp_up_time import ramp_up_time

def test_ramp_up_time_all_max():
    """If README is long, examples exist, and likes are high → score caps at 1.0."""
    rec = {
        "readme_text": "x" * 6000,                        # ≥5000 chars ⇒ readme_score = 1.0
        "example_files": ["examples/run.py", "demo.ipynb"],  # ⇒ examples_score = 1.0
        "likes": 1000,                                    # ⇒ likes_score = 1.0 (cap)
    }
    res = ramp_up_time(rec)
    assert 0.0 <= res.value <= 1.0
    assert pytest.approx(res.value, rel=1e-9) == 1.0
    assert res.details["readme_score"] == 1.0
    assert res.details["examples_score"] == 1.0
    assert res.details["likes_score"] == 1.0
    assert res.latency_ms >= 0.0

def test_ramp_up_time_weighted_combo():
    """
    README ~2500 chars → 0.5
    No examples → 0.0
    Likes 500 → 0.5
    Expected = 0.4*0.5 + 0.35*0.0 + 0.25*0.5 = 0.325
    """
    rec = {"readme_text": "x"*2500, "example_files": [], "likes": 500}
    res = ramp_up_time(rec)
    assert pytest.approx(res.value, rel=1e-6) == 0.325
    assert pytest.approx(res.details["readme_score"], rel=1e-9) == 0.5
    assert res.details["examples_score"] == 0.0
    assert pytest.approx(res.details["likes_score"], rel=1e-9) == 0.5

def test_runner_and_flatten_adds_latency_and_value():
    """Engine should run the metric and flattener should emit <name> and <name>_latency."""
    rec = {"readme_text": "readme " * 800, "example_files": ["examples/train.py"], "likes": 42}
    results = run_metrics(rec)
    flat = flatten_to_ndjson(results)
    assert "ramp_up_time" in flat
    assert "ramp_up_time_latency" in flat
    assert 0.0 <= float(flat["ramp_up_time"]) <= 1.0
    assert isinstance(flat["ramp_up_time_latency"], int)
