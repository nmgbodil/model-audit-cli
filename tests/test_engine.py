import importlib
import os
import time

import model_audit_cli.metrics_engine as metrics_engine


def test_engine_constant_output() -> None:
    """Dummy test engine."""
    ctx = {"url": "https://huggingface.co/google/gemma-3-270m/tree/main"}
    # include ska vara en mängd (set), inte en lista
    results = metrics_engine.compute_all_metrics(ctx, include={"ramp_up_time"})
    out = metrics_engine.flatten_to_ndjson(results)
    # indexera bara med str, inte tuple
    assert out["ramp_up_time"] == 1.0


def test_parallel_vs_sequential_timing() -> None:
    """Compare runtime of sequential vs parallel execution."""
    ctx = {"url": "https://huggingface.co/google/gemma-3-270m/tree/main"}

    # --- Sequential run ---
    os.environ["FORCE_SEQUENTIAL"] = "1"
    importlib.reload(metrics_engine)  # re-import to pick up env var
    start_seq = time.perf_counter()
    metrics_engine.compute_all_metrics(ctx, include={"ramp_up_time"})
    seq_time = time.perf_counter() - start_seq

    # --- Parallel run ---
    os.environ["FORCE_SEQUENTIAL"] = "0"
    importlib.reload(metrics_engine)  # re-import to pick up env var
    start_par = time.perf_counter()
    metrics_engine.compute_all_metrics(ctx, include={"ramp_up_time"})
    par_time = time.perf_counter() - start_par

    # Print times (run pytest -s to see)
    print(f"\nSequential took {seq_time:.3f} seconds")
    print(f"Parallel   took {par_time:.3f} seconds")

    # Allow some tolerance (parallel should not be slower than 1.5x sequential)
    assert par_time <= seq_time * 1.5
