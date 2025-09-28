import time
from typing import Any, Dict

from .base_metric import Metric


class RampUpTime(Metric):
    """Calculate the ramp-up time score for a model."""

    def __init__(self) -> None:
        super().__init__(name="ramp_up_time")

    def compute(self, model: Dict[str, Any]) -> "RampUpTime":
        """Compute ramp-up time score and latency.

        Args:
            model: Dictionary with possible keys:
                - "readme_text": str (contents of README)
                - "likes": int (number of likes)

        Returns:
            A tuple containing:
                - score (float): final ramp-up time score in [0,1]
                - latency_ms (float): computation time in milliseconds
        """
        t0 = time.perf_counter()

        readme_text: str = model.get("readme_text", "")
        example_files: list[str] = model.get("example_files", [])
        likes: int = model.get("likes", 0)

        readme_score = min(len(readme_text) / 5000.0, 1.0)
        examples_score = (
            1.0
            if any(
                f.endswith(".ipynb") or "example" in f.lower() for f in example_files
            )
            else 0.0
        )
        likes_score = min(likes / 1000.0, 1.0)

        self.value = 0.4 * readme_score + 0.35 * examples_score + 0.25 * likes_score
        self.latency_ms = (time.perf_counter() - t0) * 1000.0
        self.details = {}

        return self

def ramp_up_time(model: dict[str, Any]) -> RampUpTime:
    """Compatibility wrapper so tests calling ramp_up_time(model) still work."""
    return RampUpTime().compute(model)
