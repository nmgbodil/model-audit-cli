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

        with model.model.open_file() as repo:
            readme = repo.read_text("README.md", errors="ignore")
            models = repo.get_number("models")

        readme_score = min(len(readme) / 5000.0, 1.0)
        models_score = min(models / 10.0, 1.0) 
    

        # Final score: weighted average
        self.value = 0.6 * readme_score + 0.4 * models_score
        self.latency_ms = (time.perf_counter() - t0) * 1000.0
        self.details = {
            "readme_length": len(readme),
            "num_models": models,
            "readme_score": readme_score,
            "models_score": models_score,
        }

        return self

def ramp_up_time(model: dict[str, Any]) -> RampUpTime:
    """Compatibility wrapper so tests calling ramp_up_time(model) still work."""
    return RampUpTime().compute(model)
