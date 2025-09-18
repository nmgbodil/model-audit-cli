import time
from .types import MetricResult, register

@register("ramp_up_time")
def ramp_up_time(model: dict) -> MetricResult:
    t0 = time.perf_counter()

    readme_text = model.get("readme_text") or ""
    readme_score = min(len(readme_text) / 5000.0, 1.0)

    example_files = model.get("example_files") or []
    examples_score = 1.0 if any(
        f.endswith(".ipynb") or "example" in f.lower()
        for f in example_files
    ) else 0.0

    likes = int(model.get("likes") or 0)
    likes_score = min(likes / 1000.0, 1.0)

    score = 0.4*readme_score + 0.35*examples_score + 0.25*likes_score
    latency_ms = (time.perf_counter() - t0) * 1000.0

    return MetricResult(
        "ramp_up_time", float(score), latency_ms,
        {"readme_score": readme_score, "examples_score": examples_score, "likes_score": likes_score}
    )
