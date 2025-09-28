import time
from typing import Any, Mapping, Optional

from model_audit_cli.metrics.types import MetricResult, register


@register("ramp_up_time")
def ramp_up_time(model: Mapping[str, Any], readme_file: Optional[str] = None) -> dict:
    """Compute ramp-up time score.

    Args:
        model: The model metadata to evaluate.
        readme_file: The content of the README file or the file name.

    Returns:
        dict: Dictionary containing the score and latency to match the Metrics class.
    """
    t0 = time.perf_counter()

    # Read README content if a file name is provided
    if readme_file and isinstance(readme_file, str):
        try:
            with open(readme_file, "r", encoding="utf-8") as file:
                readme_text = file.read()
        except FileNotFoundError:
            readme_text = ""
    else:
        readme_text = model.get("readme_text") or ""

    # Calculate readme score
    readme_score = min(len(readme_text) / 5000.0, 1.0)

    # Calculate examples score
    example_files = model.get("example_files") or []
    examples_score = (
        1.0
        if any(f.endswith(".ipynb") or "example" in f.lower() for f in example_files)
        else 0.0
    )

    # Calculate likes score
    likes = int(model.get("likes") or 0)
    likes_score = min(likes / 1000.0, 1.0)

    # Compute final score
    score = 0.4 * readme_score + 0.35 * examples_score + 0.25 * likes_score

    # Calculate latency
    latency_ms = (time.perf_counter() - t0) * 1000.0

    # Return a dictionary matching the Metrics class structure
    return {
        "ramp_up_time": float(score),
        "ramp_up_time_latency": int(latency_ms),
    }